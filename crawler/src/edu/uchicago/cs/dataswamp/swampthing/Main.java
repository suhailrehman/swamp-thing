package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;
import java.net.URISyntaxException;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeoutException;
import java.util.regex.Pattern;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;

public class Main {

	private static final String CRAWL_QUEUE_NAME = "crawl";
	private static final String DISCOVER_QUEUE_NAME = "discover";

	public static List<Pattern> createPatternArray(String patternFile)
			throws ParserConfigurationException, XPathExpressionException, SAXException, IOException {

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document doc = builder.parse(patternFile);

		XPathFactory xFactory = XPathFactory.newInstance();
		XPath xpath = xFactory.newXPath();
		XPathExpression expr = xpath.compile("//exclude/text()");
		Object result = expr.evaluate(doc, XPathConstants.NODESET);

		NodeList nodes = (NodeList) result;
		List<Pattern> patternArray = new ArrayList<Pattern>();
		for (int i = 0; i < nodes.getLength(); i++) {
			// System.out.println("Pattern: " + nodes.item(i).getNodeValue());
			patternArray.add(Pattern.compile(nodes.item(i).getNodeValue()));
		}

		return patternArray;

	}

	public static List<Path> createPathArray(String patternFile)
			throws ParserConfigurationException, XPathExpressionException, SAXException, IOException {

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document doc = builder.parse(patternFile);

		XPathFactory xFactory = XPathFactory.newInstance();
		XPath xpath = xFactory.newXPath();
		XPathExpression expr = xpath.compile("//path/text()");
		Object result = expr.evaluate(doc, XPathConstants.NODESET);

		NodeList nodes = (NodeList) result;
		List<Path> pathArray = new ArrayList<Path>();
		for (int i = 0; i < nodes.getLength(); i++) {
			// System.out.println("Pattern: " + nodes.item(i).getNodeValue());
			pathArray.add(new Path(nodes.item(i).getNodeValue()));
		}

		return pathArray;

	}

	public static void recursiveTest(String[] args) throws Exception {

		// pickup config files off classpath
		Configuration conf = new Configuration();
		conf.addResource(new Path("/etc/hadoop/conf/core-site.xml"));

		FileSystem fs = FileSystem.get(conf);

		// TODO: Parse Command Line or Configuration Files here

		// Parse Exclusion Regex List
		List<Pattern> patterns = createPatternArray("config.xml");
		List<Path> paths = createPathArray("config.xml");

		Crawler crawler = new Crawler(fs, paths, patterns);
		crawler.startRecursiveCrawl();

		Gson gson = new GsonBuilder().setPrettyPrinting().create();
		System.out.println(gson.toJson(crawler.getDiscoveredItems()));

	}

	public static Connection getRabbitConnection()
			throws KeyManagementException, NoSuchAlgorithmException, URISyntaxException, IOException, TimeoutException {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("localhost");
		return factory.newConnection();
	}

	public static void main(String[] args) throws Exception {
		
		// pickup config files off classpath
		Configuration conf = new Configuration();
		//conf.addResource(new Path("/etc/hadoop/conf/core-site.xml"));
		
		FileSystem fs = FileSystem.get(conf);
		
		Connection connection = getRabbitConnection();
		
		System.out.println("Listening for Incoming Crawl Jobs");
		
	    Channel channel = connection.createChannel();
	    
	    Gson gson = new GsonBuilder().setDateFormat("yyyy-MM-dd'T'HH:mm:ss").create();
	    
	    channel.queueDeclare(CRAWL_QUEUE_NAME, false, false, false, null);
	    channel.queueDeclare(DISCOVER_QUEUE_NAME, false, false, false, null);
		
	    channel.basicConsume(CRAWL_QUEUE_NAME, true, "myConsumerTag",
	    		new DefaultConsumer(channel) {
	    	@Override
	    	public void handleDelivery(String consumerTag,
	    			Envelope envelope,
	    			AMQP.BasicProperties properties,
	    			byte[] body)
	    					throws IOException
	    	{
	    		String message = new String(body, "UTF-8");
	    		System.out.println(" [x] Received '" + message + "'");

	    		CrawlJobSpec spec = gson.fromJson(message, CrawlJobSpec.class);
	    		UUID last_crawl = UUID.fromString(gson.fromJson(message, JsonObject.class).get("last_crawl").getAsString());

	    		Crawler crawler = new Crawler(fs);
	    		crawler.addExclusionPattern(Pattern.compile(spec.getExclusion_patterns()));
	    		crawler.setLast_crawl(last_crawl);

	    		crawler.crawlTarget(spec);
	    		

	    		// TODO: Send discovered items into discovered queue
	    		for (CrawledItem item : crawler.getDiscoveredFiles()) {
	    			channel.basicPublish("", DISCOVER_QUEUE_NAME, null, gson.toJson(item).getBytes());
	    		}

	    		if (spec.getCrawl_depth() > 0) {

	    			// TODO: Send discovered directories into crawl queue depth
	    			for (CrawledItem item : crawler.getDiscoveredDirectories()) {
	    				System.out.println("New DIR: "+item.getPath());
	    				CrawlJobSpec newspec = new CrawlJobSpec(spec.getUuid(), spec.getLake(), item.getPath(),
	    						spec.getCrawl_depth() - 1, spec.getExclusion_patterns());
	    				
	    				JsonElement jsonElement = gson.toJsonTree(newspec);
	    				jsonElement.getAsJsonObject().addProperty("last_crawl", last_crawl.toString());
	    				
	    				channel.basicPublish("", CRAWL_QUEUE_NAME, null, gson.toJson(jsonElement).getBytes());
	    			}
	    		}

	    		// DEBUG
	    		// System.out.println(gson.toJson(crawler.getDiscoveredItems()));

	    		// TODO: (process the message components here ...)
	    	}});

		
				
	}
}
