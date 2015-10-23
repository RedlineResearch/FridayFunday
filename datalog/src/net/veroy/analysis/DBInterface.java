package net.veroy.analysis;
import java.util.Vector;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;
import java.sql.Connection;



public class DBInterface {
    private final static String pointer_table = "pointers";
    private final static String object_table = "objects";
    private final Connection conn;
    private final Vector<String> statement_buffer;

    DBInterface(Connection conn) {
        this.conn = conn;
        statement_buffer = new Vector(10000);

        statement_buffer.add( String.format( "DROP TABLE IF EXISTS %s", pointer_table ) );
        statement_buffer.add(String.format( "CREATE TABLE %s " +
                    "( fromId INTEGER," +
                    "  tgtId INTEGER," +
                    "  startTime INTEGER," +
                    "  endTime INTEGER )",
                    pointer_table ));
        statement_buffer.add( String.format( "DROP TABLE IF EXISTS %s", object_table ) );
        statement_buffer.add(String.format( "CREATE TABLE %s " +
                    "( objId INTEGER," +
                    "  type STRING," +
                    "  allocTime INTEGER," +
                    "  deathTime INTEGER )",
                    object_table ));
    }



    void insertPointer(int from_id, int to_id, int start_time, int end_time) {
        statement_buffer.add( String.format( "INSERT OR REPLACE INTO %s" +
                    "(fromId,tgtId,startTime,endTime) " +
                    " VALUES (%d,%d,%d,%d)",
                    pointer_table,
                    from_id,
                    to_id,
                    start_time,
                    end_time ) );


    }

    void insertObject(int id, String type, int allocTime, int deathTime) {
        statement_buffer.add( String.format( "INSERT OR REPLACE INTO %s" +
                                             "(objId,type,allocTime,deathTime) " +
                                             " VALUES (%d,'%s',%d,%d)",
                                             object_table,
                                             id,
                                             type.replace(";",""),
                                             allocTime,
                                             deathTime ) );
    }  

    void executeUpdate() throws SQLException {
        for (String update : statement_buffer) {
            Statement stmt = this.conn.createStatement();
            stmt.executeUpdate(update);
        }
    }
}
