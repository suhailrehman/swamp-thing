package edu.uchicago.cs.dataswamp.swampthing;

import static org.junit.Assert.*;

import java.io.IOException;
import java.util.UUID;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestWatcher;

@SuppressWarnings("unused")
public class CrawlerTest {
	
	private Configuration conf;
	private FileSystem fs;

	@Rule
    public TestWatcher watchman = new Log4jTestWatcher(this.getClass());
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
		//Set up Apache FileIO
		this.conf = new Configuration();
		this.fs = FileSystem.get(conf);
	}

	@After
	public void tearDown() throws Exception {
	}

	@Ignore("Not yet implemented")
	@Test
	public void testCrawlTarget() {
	}

	@Ignore("Not yet implemented")
	@Test
	public void testGetDiscoveredItems() {
	}

	@Ignore("Not yet implemented")
	@Test
	public void testGetDiscoveredDirectories() {
	}

	@Ignore("Not yet implemented")
	@Test
	public void testGetDiscoveredFiles() {
	}

	@Ignore("Not yet implemented")
	@Test
	public void testCheckStringMatch() throws IOException
	{
		
		CrawlJobSpec exclude = new CrawlJobSpec(UUID.randomUUID(), "GlobusLake", "/folder/.gitignore", 1, "(.*)(/\\.)(.*)"); 
		CrawlJobSpec include = new CrawlJobSpec(UUID.randomUUID(), "GlobusLake", "/folder/importantfile", 1, "(.*)(/\\.)(.*)"); 
		
		Crawler crawler = new Crawler(this.fs);
		crawler.addExclusionPattern(Pattern.compile(exclude.getExclusion_patterns()));
		
		crawler.crawlTarget(exclude);
		
	}
	
}
