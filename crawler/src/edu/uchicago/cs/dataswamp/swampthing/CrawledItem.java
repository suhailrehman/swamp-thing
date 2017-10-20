package edu.uchicago.cs.dataswamp.swampthing;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.UUID;
import javax.persistence.Entity;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;


@Entity(name = "crawled_item")
public class CrawledItem {
	
	/*("id", "lake", "path", "directory", "size",
            "last_modified", "owner", "last_crawl")
    */
    public static final long HEADER_SIZE = 4096L;

	private UUID last_crawl;
	private String lake;
	private String path;
	private long size;
	private boolean directory;
	private String owner;
	private String group;
	private long last_modified;
	//private String fs_scheme;
	//private String fs_uri;
	//private String header_path;
	

	@SuppressWarnings("unused")
	private void copyHDFStoLocal(String hdfspath, String localpath, FileSystem fs, long size) throws IOException
	{
		InputStream is = fs.open(new Path(hdfspath));
        OutputStream os = new BufferedOutputStream(new FileOutputStream(localpath));
        IOUtils.copyBytes(is, os, fs.getConf());	
        IOUtils.copyBytes(is, os, size, true);
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
		this.last_modified = filestatus.getModificationTime();
		
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
		return last_modified;
	}

	
	@Override
	public String toString() {
		return "CrawledItem [job_uuid=" + last_crawl + ", path=" + path + ", file_size=" + size + ", is_directory="
				+ directory + ", owner=" + owner + ", group=" + group + ", modification_time=" + last_modified
				+ "]";
	}
	
	

}
