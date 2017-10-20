package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import javax.persistence.EntityManager;
import javax.persistence.EntityTransaction;
import javax.persistence.Persistence;

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

	public void addPath(Path path) {
		this.crawlPaths.add(path);	
	}
	
	public void addExclusionPattern(Pattern pattern){
		this.exclusionPatterns.add(pattern);
	}
	
	private boolean checkStringMatch(String line, List<Pattern> patternList)
	{
		for(Pattern pattern: patternList)
		{
			Matcher m = pattern.matcher(line);
			if(m.find())
				return true;
		}
		return false;
	}
	
	public void startRecursiveCrawl() throws IOException
	{
		//ORM Setup
		EntityManager entityManager = Persistence.createEntityManagerFactory("crawled-item").createEntityManager();
		EntityTransaction txn = entityManager.getTransaction();
		

		for(Path path : this.crawlPaths)
		{
			// the second boolean parameter here sets the recursion to true
			RemoteIterator<LocatedFileStatus> fileStatusListIterator = this.filesystem.listFiles(path, true);
			while (fileStatusListIterator.hasNext()) {
				LocatedFileStatus fileStatus;
				try {
					fileStatus = fileStatusListIterator.next();
				
					String fullPath = fileStatus.getPath().toString();
					if(!checkStringMatch(fullPath, this.exclusionPatterns))
					{
						txn.begin();
						CrawledItem item = new CrawledItem(this.filesystem, fileStatus);
						this.discoveredItems.add(item);
						entityManager.persist(item);
						txn.commit();

					}
				} catch (IOException e) {
					//TODO Handle Crawl IO exceptions here
					System.err.println("WARNING, unable to crawl path: "+ path.toString());
					//e.printStackTrace();
				}
					
			}
		}
		
		entityManager.close();
		
	}

	public void crawlTarget(CrawlJobSpec jobspec) throws IOException {

		FileStatus[] files = this.filesystem.listStatus(new Path(jobspec.getUri()));
		
		for (FileStatus fileStatus : files) {
				String fullPath = fileStatus.getPath().toString();
				if (!checkStringMatch(fullPath, this.exclusionPatterns)) {
					CrawledItem item = new CrawledItem(this.filesystem, jobspec.getUuid(), jobspec.getLake(), fileStatus);
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
