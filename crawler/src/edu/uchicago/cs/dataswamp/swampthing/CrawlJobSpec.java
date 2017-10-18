package edu.uchicago.cs.dataswamp.swampthing;

import java.util.UUID;

public class CrawlJobSpec {
	
	UUID uuid;
	String lake;
	String root_uri;
	Integer crawl_depth;
	String exclusion_patterns;
	
	public String getExclusion_patterns() {
		return exclusion_patterns;
	}

	public void setExclusion_patterns(String exclusion_patterns) {
		this.exclusion_patterns = exclusion_patterns;
	}

	public UUID getUuid() {
		return uuid;
	}

	public void setUuid(UUID uuid) {
		this.uuid = uuid;
	}

	public String getLake() {
		return lake;
	}

	public void setLake(String lake) {
		this.lake = lake;
	}

	public String getUri() {
		return root_uri;
	}

	public void setUri(String uri) {
		this.root_uri = uri;
	}

	public Integer getCrawl_depth() {
		return crawl_depth;
	}

	public void setCrawl_depth(Integer crawl_depth) {
		this.crawl_depth = crawl_depth;
	}

	public CrawlJobSpec(UUID uuid, String lake, String uri, Integer crawl_depth, String exclusion_patterns) {
		super();
		this.uuid = uuid;
		this.lake = lake;
		this.root_uri = uri;
		this.crawl_depth = crawl_depth;
		this.exclusion_patterns = exclusion_patterns;
	}

}
