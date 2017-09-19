package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
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

public class Main {
	
	public static List<Pattern> createPatternArray(String patternFile) throws ParserConfigurationException, XPathExpressionException, SAXException, IOException
	{
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
	    DocumentBuilder builder =  factory.newDocumentBuilder();
	    Document doc = builder.parse(patternFile);

	    XPathFactory xFactory = XPathFactory.newInstance();
	    XPath xpath = xFactory.newXPath();
	    XPathExpression  expr = xpath.compile("//exclude/text()");
	    Object result = expr.evaluate(doc, XPathConstants.NODESET);

	    NodeList nodes = (NodeList) result;
	    List<Pattern> patternArray = new ArrayList<Pattern>();
	    for(int i=0; i<nodes.getLength();i++)
	    {
	    	//System.out.println("Pattern: " + nodes.item(i).getNodeValue());
	    	patternArray.add(Pattern.compile(nodes.item(i).getNodeValue()));
	    }
	    
	    return patternArray;

	}
	
	public static List<Path> createPathArray(String patternFile) throws ParserConfigurationException, XPathExpressionException, SAXException, IOException
	{
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
	    DocumentBuilder builder =  factory.newDocumentBuilder();
	    Document doc = builder.parse(patternFile);

	    XPathFactory xFactory = XPathFactory.newInstance();
	    XPath xpath = xFactory.newXPath();
	    XPathExpression  expr = xpath.compile("//path/text()");
	    Object result = expr.evaluate(doc, XPathConstants.NODESET);

	    NodeList nodes = (NodeList) result;
	    List<Path> pathArray = new ArrayList<Path>();
	    for(int i=0; i<nodes.getLength();i++)
	    {
	    	//System.out.println("Pattern: " + nodes.item(i).getNodeValue());
	    	pathArray.add(new Path(nodes.item(i).getNodeValue()));
	    }
	    
	    return pathArray;

	}
	
	public static boolean checkStringMatch(String line, List<Pattern> patternList)
	{
		//TODO: Compile out of band to make it more efficient
		for(Pattern pattern: patternList)
		{
			Matcher m = pattern.matcher(line);
			if(m.find())
				return true;
		}
		return false;
	}

	public static void main(String[] args) throws Exception {

		// pickup config files off classpath
		Configuration conf = new Configuration();
		conf.addResource(new Path("/etc/hadoop/conf/core-site.xml"));
				
		FileSystem fs = FileSystem.get(conf);
		
		//TODO: Parse Command Line or Configuration Files here
		
		//Parse Exclusion Regex List
		List<Pattern> patterns = createPatternArray("config.xml");
		List<Path> paths = createPathArray("config.xml");
		

		for(Path path : paths)
		{
			// the second boolean parameter here sets the recursion to true
			RemoteIterator<LocatedFileStatus> fileStatusListIterator = fs.listFiles(path, true);
			while (fileStatusListIterator.hasNext()) {
				LocatedFileStatus fileStatus = fileStatusListIterator.next();
				// do stuff with the file like ...
				String fullPath = fileStatus.getPath().toString();
				if(!checkStringMatch(fullPath, patterns))
					System.out.println(fullPath);
			}
		}

	}

}
