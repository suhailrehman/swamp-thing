package edu.uchicago.cs.dataswamp.swampthing;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;

public class Main {

	public static void main(String[] args) throws IOException {
		FileSystem fs = FileSystem.get(new Configuration());
		
		//TODO: Parse Command Line or Configuration Files here

		// the second boolean parameter here sets the recursion to true
		RemoteIterator<LocatedFileStatus> fileStatusListIterator = fs.listFiles(new Path("."), true);
		while (fileStatusListIterator.hasNext()) {
			LocatedFileStatus fileStatus = fileStatusListIterator.next();
			// do stuff with the file like ...
			System.out.println(fileStatus.getPath().toString());
		}

	}

}
