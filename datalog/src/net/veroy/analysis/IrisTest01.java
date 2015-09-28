/**
 * 
 */
package net.veroy.analysis;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.deri.iris.Configuration;
import org.deri.iris.EvaluationException;
import org.deri.iris.KnowledgeBaseFactory;
import org.deri.iris.api.IKnowledgeBase;
import org.deri.iris.api.basics.IQuery;
import org.deri.iris.api.basics.IRule;
import org.deri.iris.api.terms.IVariable;
import org.deri.iris.compiler.Parser;
import org.deri.iris.compiler.ParserException;
import org.deri.iris.storage.IRelation;

/**
 * @author rveroy
 *
 */
public class IrisTest01 {

    /**
     * @param args
     */
    public static void main(String[] args) {
        Configuration config = KnowledgeBaseFactory.getDefaultConfiguration();
        Parser parser = new Parser();
        IKnowledgeBase kbase;

	String pathToTrace = null;
	if(args.length > 0)
	    pathToTrace = args[0];

        /*String program = "man('homer').\n" +
                          "woman('marge').\n" +
                          "hasSon('homer','bart').\n" +
                          "isMale(?x) :- man(?x).\n" +
                          "isFemale(?x) :- woman(?x).\n" +
                          "isMale(?y) :- hasSon(?x,?y).\n" +
                          "?-isMale(?x).\n"+
                          "?-hasSon('homer',?x).";*/
       /* String program = //"pointsTo('A3',2,9).\n" +
                        "pointsTo('A1','A2',0,6).\n" +
                         "pointsTo('A3','A2',2,9).\n" +
                         "pointsTo('A2','A4',2,7).\n" +
                         "pointsTo('A5','A1',1,5).\n" +
                         "pointsTo('A1','A4',7,9).\n" +
                         "pointsTo('A3','A4',10,14).\n" +
                         "timestamp(0). \n" +
                         "timestamp(?t) :- ?s + 1 = ?t, timestamp(?s), ?t <= 14. \n" +
                         "pointsToInstant(?A,?B,?T) :- timestamp(?T), pointsTo(?A,?B,?S,?E), ?T >= ?S, ?E >= ?T.\n" +
                         // TODO These are queries that worked. I used them to eventually develop the query I wanted.
                         // "?-pointsTo('A3',?Z1,?ST3,?ET3),pointsTo('A1', ?Z2, ?ST1, ?ET1),?Z1=?Z2,?ST3>=?ST1.\n" +
                         /// "?-pointsToInstant('A1',?Z1,?T).\n" +
                         // "?-timestamp(?T), pointsToInstant('A3',?Z, ?T), pointsToInstant('A1', ?Z, ?T).\n" +
                         // "?-timestamp(?T), pointsToInstant(?X ,?Z, ?T), pointsToInstant(?Y, ?Z, ?T).\n" +
                         // TODO: End
                         "?-timestamp(?T), pointsToInstant(?X ,?Z, ?T), pointsToInstant(?Y, ?Z, ?T), ?X != ?Y.\n";
        */


	try (
                InputStreamReader isr = new InputStreamReader(System.in, Charset.forName("UTF-8"));
                BufferedReader bufreader = new BufferedReader(isr);
        		) {
	        		String line;
	        		String program = ETParser.processInput(pathToTrace);
				System.out.println("Parse success. Please enter your queries.");
				System.out.println("Enter Ctrl-D to cease input.");
				System.out.print("> ");
	        		while ((line = bufreader.readLine()) != null) {
	        		  program += line;
	        		  program += "\n";
				  System.out.print("> ");
	        		}
				parser.parse(program);
        }
        catch (ParserException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (IOException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage() );
            System.exit(0);
        }
        try {
             kbase = KnowledgeBaseFactory.createKnowledgeBase( parser.getFacts(),
                                                               parser.getRules(),
                                                               config );

        } catch (EvaluationException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            return;
        }
        List<IQuery> queryList = parser.getQueries();
	System.err.println(parser.getRules().size());
	for(Iterator<IRule> iter = parser.getRules().iterator(); iter.hasNext(); ){
	    System.err.println(iter.next());
	}
        int num = 0;
        for (Iterator<IQuery> iter = queryList.iterator(); iter.hasNext(); ) {
            IQuery query = iter.next();
            IRelation result;
            ArrayList<IVariable> vars = new ArrayList<IVariable>();
            try {
                result = kbase.execute(query,vars);
            } catch (EvaluationException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                return;
            }
            System.out.println(String.format("Query %d:", num));
            System.out.println(query.toString());
            System.out.println(vars);
            System.out.println(result.size());
            for (int i = 0; i < result.size(); ++i) {
                System.out.println(result.get(i).toString());
         
            }
            num += 1;
        }
    }
}
