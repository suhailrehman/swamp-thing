package edu.uchicago.cs.dataswamp.swampthing;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.UUID;
import javax.persistence.Entity;
import javax.persistence.Id;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocatedFileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;


@Entity(name = "crawled-item")
public class CrawledItem {
	
    public static final long HEADER_SIZE = 4096L;

	@Id
	private UUID uuid;
	private String path;
	private long file_size;
	private boolean is_directory;
	private String owner;
	private String group;
	private long modification_time;
	private String fs_scheme;
	private String fs_uri;
	private String header_path;
	

	@SuppressWarnings("unused")
	private void copyHDFStoLocal(String hdfspath, String localpath, FileSystem fs, long size) throws IOException
	{
		InputStream is = fs.open(new Path(hdfspath));
        OutputStream os = new BufferedOutputStream(new FileOutputStream(localpath));
        IOUtils.copyBytes(is, os, fs.getConf());	
        IOUtils.copyBytes(is, os, size, true);
	}
	
	public CrawledItem(FileSystem fs, LocatedFileStatus filestatus, String header_path_prefix)
	{
		super();
		this.uuid = UUID.randomUUID();
		this.path = filestatus.getPath().toString();
		this.file_size = filestatus.getLen();
		this.is_directory = filestatus.isDirectory();
		this.owner = filestatus.getOwner();
		this.group = filestatus.getGroup();
		this.modification_time = filestatus.getModificationTime();
		this.fs_scheme = fs.getScheme();
		this.fs_uri = fs.getUri().toString();
		this.header_path = header_path_prefix + "/" + this.uuid.toString();
		
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


	public UUID getUuid() {
		return uuid;
	}


	public String getPath() {
		return path;
	}


	public long getFile_size() {
		return file_size;
	}


	public boolean isIs_directory() {
		return is_directory;
	}


	public String getOwner() {
		return owner;
	}


	public String getGroup() {
		return group;
	}


	public long getModification_time() {
		return modification_time;
	}


	public String getFs_scheme() {
		return fs_scheme;
	}


	public String getFs_uri() {
		return fs_uri;
	}
	
	/*
	public String getHeader_path() {
		return header_path;
	}
	*/
	
	@Override
	public String toString() {
		return "CrawledItem [uuid=" + uuid + ", path=" + path + ", file_size=" + file_size + ", is_directory="
				+ is_directory + ", owner=" + owner + ", group=" + group + ", modification_time=" + modification_time
				+ ", fs_scheme=" + fs_scheme + ", fs_uri=" + fs_uri + ", header_path=" + header_path + "]";
	}
	
	

}