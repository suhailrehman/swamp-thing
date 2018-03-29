package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;


import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocatedFileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.RemoteIterator;

public class Crawler {
	
	FileSystem filesystem;
	List<Path> crawlPaths;
	List<Pattern> exclusionPatterns;
	List<CrawledItem> discoveredItems = new ArrayList<CrawledItem>();
	String s3bucket;
	String s3prefix;
	UUID last_crawl;
	
	public Crawler(FileSystem fs) {
		super();
		this.filesystem = fs;
		this.crawlPaths = new ArrayList<Path>();
		this.exclusionPatterns = new ArrayList<Pattern>();
	}
	
	public Crawler(FileSystem fs, List<Path> crawlpaths, List<Pattern> exclusionPatterns)
	{
		super();
		this.filesystem = fs;
		this.crawlPaths= crawlpaths;
		this.exclusionPatterns = exclusionPatterns;
	}

	public UUID getLast_crawl() {
		return last_crawl;
	}

	public void setLast_crawl(UUID last_crawl) {
		this.last_crawl = last_crawl;
	}

	public String getS3bucket() {
		return s3bucket;
	}

	public void setS3bucket(String s3bucket) {
		this.s3bucket = s3bucket;
	}

	public String getS3prefix() {
		return s3prefix;
	}

	public void setS3prefix(String s3prefix) {
		this.s3prefix = s3prefix;
	}

	public void addPath(Path path) {
		this.crawlPaths.add(path);	
	}
	
	public void addExclusionPattern(Pattern pattern){
		this.exclusionPatterns.add(pattern);
	}
	
	private boolean checkStringMatch(String line)
	{
		for(Pattern pattern: this.exclusionPatterns)
		{
			Matcher m = pattern.matcher(line);
			if(m.find())
				return true;
		}
		return false;
	}
	
	@Deprecated //Recursive crawl does not emit directories.
	public void startRecursiveCrawl() throws IOException
	{
		
		for(Path path : this.crawlPaths)
		{
			// the second boolean parameter here sets the recursion to true
			RemoteIterator<LocatedFileStatus> fileStatusListIterator = this.filesystem.listFiles(path, true);
			while (fileStatusListIterator.hasNext()) {
				LocatedFileStatus fileStatus;
				try {
					fileStatus = fileStatusListIterator.next();
				
					String fullPath = fileStatus.getPath().toString();
					if(!checkStringMatch(fullPath))
					{
						CrawledItem item = new CrawledItem(this.filesystem, fileStatus);
						this.discoveredItems.add(item);
					}
				} catch (Exception e) {
					//TODO Handle Crawl IO exceptions here
					System.err.println("WARNING, unable to crawl path: "+ path.toString());
					//e.printStackTrace();
				}
					
			}
		}
				
	}

	public void crawlTarget(CrawlJobSpec jobspec) throws IOException {

		FileStatus[] files = this.filesystem.listStatus(new Path(jobspec.getUri()));
		
		for (FileStatus fileStatus : files) {
				String fullPath = fileStatus.getPath().toString();
				if (!checkStringMatch(fullPath)) {
					CrawledItem item;
					if(this.s3bucket != null || !this.s3bucket.isEmpty())
					{
						item = new CrawledItem(this.filesystem, this.getLast_crawl(), jobspec.getLake(), fileStatus, this.s3bucket, this.s3prefix, true);
					}
					else
					{
						item = new CrawledItem(this.filesystem, this.getLast_crawl(), jobspec.getLake(), fileStatus);
					}
					this.discoveredItems.add(item);
				}
		}

	}

	public List<CrawledItem> getDiscoveredItems() {
		return discoveredItems;
	}
	
	public List<CrawledItem> getDiscoveredDirectories()
	{
	    return discoveredItems.stream().filter(u -> u.isDirectory()).collect(Collectors.toList());

	}
	
	public List<CrawledItem> getDiscoveredFiles()
	{
	    return discoveredItems.stream().filter(u -> !(u.isDirectory())).collect(Collectors.toList());

	}


}
