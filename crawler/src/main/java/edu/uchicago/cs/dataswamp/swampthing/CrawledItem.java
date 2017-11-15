package edu.uchicago.cs.dataswamp.swampthing;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;


public class CrawledItem {
	
    public static final long HEADER_SIZE = 4096L;
	private static final Logger logger = LogManager.getLogger(CrawledItem.class);


	private UUID last_crawl;
	private String lake;
	private String path;
	private long size;
	private boolean directory;
	private String owner;
	private String group;
	private Date last_modified;
	private byte[] head_4k; //Raw 4k byte array of file contents.
	
	@SuppressWarnings("unused")
	private void copyHDFStoLocal(String hdfspath, String localpath, FileSystem fs, long size) throws IOException
	{
		InputStream is = fs.open(new Path(hdfspath));
        OutputStream os = new BufferedOutputStream(new FileOutputStream(localpath));
        IOUtils.copyBytes(is, os, fs.getConf());	
        IOUtils.copyBytes(is, os, size, true);
	}
	
	
	public byte[] get4khead(FileSystem fs)
	{
		//TODO: Check if this object is valid
		if(!this.directory)
		{
			try
			{
				int read_size = (int) (this.size>HEADER_SIZE?HEADER_SIZE:this.size);
				this.head_4k = new byte[read_size];
				InputStream is = fs.open(new Path(path));
				is.read(this.head_4k, 0, read_size);
				is.close();
			}
			catch (org.apache.hadoop.security.AccessControlException e) {
				logger.warn("No permissions to read: "+ this.path);
			} catch (IllegalArgumentException | IOException e) {
				logger.warn("I/O Error reading: "+ this.path);
			}
		}
		
		return this.head_4k;
		
	}
	
	public CrawledItem() {
		super();
		// TODO Auto-generated constructor stub
	}

	public CrawledItem(FileSystem fs, FileStatus filestatus)
	{
		super();
		this.path = filestatus.getPath().toString();
		this.size = filestatus.getLen();
		this.directory = filestatus.isDirectory();
		this.owner = filestatus.getOwner();
		this.group = filestatus.getGroup();
		this.last_modified = Date.from(Instant.ofEpochMilli(filestatus.getModificationTime()));
		this.head_4k = null;
		/*
		if(!this.is_directory)
		{
			try {
				copyHDFStoLocal(this.path, this.header_path, fs, HEADER_SIZE);
			} catch (IOException e) {
				System.err.println("WARNING, unable to copy header contents of file: "+ this.path);
				e.printStackTrace();
			}
		}
		*/
		
	}


	public CrawledItem(FileSystem fs, UUID crawl_job_uuid, String lake, FileStatus filestatus)
	{
		this(fs,filestatus);
		this.last_crawl = crawl_job_uuid;
		this.lake = lake;
		
	}
	
	

	public UUID getJobUuid() {
		return last_crawl;
	}
	
	public String getLake() {
		return lake;
	}


	public String getPath() {
		return path;
	}


	public long getFile_size() {
		return size;
	}


	public boolean isDirectory() {
		return directory;
	}


	public String getOwner_name() {
		return owner;
	}


	public String getGroup_name() {
		return group;
	}


	public long getModification_time() {
		return last_modified.getTime();
	}

	
	@Override
	public String toString() {
		return "CrawledItem [job_uuid=" + last_crawl + ", path=" + path + ", file_size=" + size + ", is_directory="
				+ directory + ", owner=" + owner + ", group=" + group + ", modification_time=" + last_modified
				+ "]";
	}
	
	

}
