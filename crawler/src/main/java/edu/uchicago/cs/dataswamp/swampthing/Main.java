package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;

import java.util.Base64;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.TimeoutException;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;

import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializer;

import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;

public class Main {
	
	private static final Logger logger = LogManager.getLogger(Main.class);
		
	public static Connection getRabbitConnection(Properties props)
			throws KeyManagementException, NoSuchAlgorithmException, URISyntaxException, IOException, TimeoutException {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost(props.getProperty("rabbitServer"));
		factory.setUsername(props.getProperty("rabbitUser"));
		factory.setPassword(props.getProperty("rabbitPassword"));
		factory.setVirtualHost(props.getProperty("rabbitServer"));
		return factory.newConnection();
	}

	public static void main(String[] args) throws Exception {
		
		//Load crawler properties file
		Properties props = new Properties();
		props.load(Main.class.getResourceAsStream("/config.properties"));
		
		//TODO: Check if $HADOOP_HOME is defined, if not, pass a warning about local HDFS access
		
		Configuration conf = new Configuration();
		
		//Set up RabbitMQ connections
		Connection connection = getRabbitConnection(props);
		Channel channel = connection.createChannel();
	    
	    //Register date and byte serialization (Base64) formats
	    GsonBuilder builder = new GsonBuilder(); 
	    builder.setDateFormat("yyyy-MM-dd'T'HH:mm:ss");
		builder.registerTypeAdapter(byte[].class, (JsonSerializer<byte[]>) (src, typeOfSrc, context) -> new JsonPrimitive(Base64.getEncoder().encodeToString(src)));
	    builder.registerTypeAdapter(byte[].class, (JsonDeserializer<byte[]>) (json, typeOfT, context) -> Base64.getDecoder().decode(json.getAsString()));
	    Gson gson = builder.create();
	    
	    //Declare Rabbit Queues if it does not already exist.
	    channel.queueDeclare(props.getProperty("crawlQueueName"), false, false, false, null);
	    channel.queueDeclare(props.getProperty("discoverQueueName"), false, false, false, null);
		
	    
	    logger.info("Listening for Incoming Crawl Jobs");
	    
	    channel.basicConsume(props.getProperty("crawlQueueName"), true, "myConsumerTag",
	    		new DefaultConsumer(channel) {
	    	@Override
	    	public void handleDelivery(String consumerTag,
	    			Envelope envelope,
	    			AMQP.BasicProperties properties,
	    			byte[] body)
	    					throws IOException
	    	{
	    		String message = new String(body, "UTF-8");
	    		logger.trace("Received on Crawl Queue: '" + message + "'");

	    		CrawlJobSpec spec = gson.fromJson(message, CrawlJobSpec.class);
	    		UUID last_crawl = UUID.fromString(gson.fromJson(message, JsonObject.class).get("last_crawl").getAsString());
	    		
	    		//Setup the appropriate FileSystem based on incoming URI
	    		FileSystem fs;
				try {
					fs = FileSystem.get(new URI(spec.root_uri), conf);
				

	    		Crawler crawler = new Crawler(fs);
	    		crawler.addExclusionPattern(Pattern.compile(spec.getExclusion_patterns()));
	    		crawler.setLast_crawl(last_crawl);

	    		crawler.crawlTarget(spec);
	    		
				
	    
	    		//Send discovered items (files and directories) into discovered queue
	    		for (CrawledItem item : crawler.getDiscoveredFiles()) {
	    			logger.debug("Discovered New File: "+item.getPath());
	    			item.get4khead(fs);
	    			channel.basicPublish("", props.getProperty("discoverQueueName"), null, gson.toJson(item).getBytes());
	    			
	    		}

	    		if (spec.getCrawl_depth() > 0) {

	    			//Send discovered directories into crawl queue for recursive crawl (only if depth : 0)
	    			for (CrawledItem item : crawler.getDiscoveredDirectories()) {
	    				logger.debug("Discovered New Directory: "+item.getPath());
	    				
	    				channel.basicPublish("", props.getProperty("discoverQueueName"), null, gson.toJson(item).getBytes());
	    				
	    				CrawlJobSpec newspec = new CrawlJobSpec(spec.getUuid(), spec.getLake(), item.getPath(),
	    						spec.getCrawl_depth() - 1, spec.getExclusion_patterns());
	    				
	    				JsonElement jsonElement = gson.toJsonTree(newspec);
	    				jsonElement.getAsJsonObject().addProperty("last_crawl", last_crawl.toString());
	    				
	    				channel.basicPublish("", props.getProperty("crawlQueueName"), null, gson.toJson(jsonElement).getBytes());
	    			}
	    		}
	    		
	    		

	    		
	    		logger.info(String.format("%s Crawl directory: [%s], Depth: %d, Discovered %d directories, %d files.", 
	    				fs.getScheme(),
	    				spec.getUri(),
	    				spec.getCrawl_depth(),
	    				crawler.getDiscoveredDirectories().size(),
	    				crawler.getDiscoveredFiles().size()));
	    		
				} 
				catch (URISyntaxException e) {
					logger.error("Invalid URI received: " + spec.root_uri);
					return;
				}
				catch (Exception e) {
					logger.error("Cannot Crawl Target: " + spec.root_uri);
				}
				
				
	    	}});

		
				
	}
}
