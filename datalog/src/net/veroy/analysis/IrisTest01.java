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

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;
import java.sql.Connection;

/**
 * @author rveroy
 *
 */
public class IrisTest01 {

    private final static String table = "objects";

    /**
     * @param args
     */
    public static void main(String[] args) {
        Configuration config = KnowledgeBaseFactory.getDefaultConfiguration();
        Parser parser = new Parser();
        IKnowledgeBase kbase;

        String pathToTrace = null;
        if(args.length > 0) {
            pathToTrace = args[0];
        }


        DBInterface db_interface = null;
        // TODO Check return value
        Connection conn;
        try {
            Class.forName("org.sqlite.JDBC");
            conn = DriverManager.getConnection("jdbc:sqlite:iristest.db");
            db_interface = new DBInterface(conn);
        } catch ( Exception e ) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage() );
            System.exit(0);
        }

        try (
                InputStreamReader isr = new InputStreamReader(System.in, Charset.forName("UTF-8"));
                BufferedReader bufreader = new BufferedReader(isr);
            ) {
            String line;
            String program = ETParser.processInput(pathToTrace, db_interface);
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
        catch (SQLException e) {
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
            for (int i = 0; i < result.size(); ++i) {
                System.out.println(result.get(i).toString());
            }
            num += 1;
        }
    }
}
