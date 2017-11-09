package edu.uchicago.cs.dataswamp.swampthing;

import static org.junit.Assert.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;

import org.apache.commons.io.FileUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.junit.rules.TestWatcher;

public class CrawledItemTest {

	private static final int FILE_SIZE = 1048576;
	private Configuration conf;
	private FileSystem fs;
    private File testfile;
    private byte[] randombytes;
    
    @Rule
    public TemporaryFolder folder = new TemporaryFolder();
        
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
		
		//Generate a Random File
		this.testfile = folder.newFile();
		this.randombytes = new byte[FILE_SIZE];
		new Random().nextBytes(randombytes);
		FileUtils.writeByteArrayToFile(this.testfile, randombytes);
	}

	@After
	public void tearDown() throws Exception {
		this.folder.delete();
		this.fs.close();
	}

	@Test
	public void testGet4khead() throws FileNotFoundException, IllegalArgumentException, IOException {
		
		FileStatus[] files = this.fs.listStatus(new Path(this.testfile.getAbsolutePath()));
		CrawledItem item = new CrawledItem(fs, files[0]);
		
		byte[] head_4k = item.get4khead(fs);
		
		assertArrayEquals(Arrays.copyOfRange(this.randombytes,0,4096), head_4k);
		
		
	}

}
