package net.veroy.analysis;

//import net.veroy.guava.benchmark.cache.ObjectRecord;
//import net.veroy.guava.benchmark.cache.UpdateRecord;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.math.BigInteger;
import java.nio.charset.Charset;

import java.util.zip.GZIPInputStream;
import java.util.Map;

import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.HashMap;

import org.deri.iris.api.IKnowledgeBase;
import org.deri.iris.api.basics.IQuery;
import org.deri.iris.api.terms.IVariable;
import org.deri.iris.compiler.Parser;
import org.deri.iris.compiler.ParserException;
import org.deri.iris.storage.IRelation;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;

public class ETParser {

    static HashMap<Integer, ObjectModel> heap;


    public static String processInput(String path, DBInterface db_interface) throws SQLException {
        heap = new HashMap<Integer, ObjectModel>();

        String program = "";

        try {
            int i = 0;
            String line;
            InputStreamReader isr;

            if(path == null)
                isr = new InputStreamReader(System.in, Charset.forName("UTF-8"));
            else if(path.contains(".gz"))
                isr = new InputStreamReader(new GZIPInputStream(new FileInputStream(path)));
	    else
                isr = new InputStreamReader(new FileInputStream(path));

            try (
                    BufferedReader bufreader = new BufferedReader(isr);
                ) {
                int timeByMethod = 0;
                while ((line = bufreader.readLine()) != null) {
                    // Deal with the line
                    String[] fields = line.split(" ");
                    if (isAllocation(fields[0])) {
                        ObjectRecord rec = parseAllocation( fields, timeByMethod );
                        heap.put( rec.get_objId(),
                                  new ObjectModel( rec.get_objId(),
                                                   rec.get_type(),
                                                   timeByMethod ) );
                    }
                    else if (isUpdate(fields[0])) {
                        timeByMethod++;
                        UpdateRecord rec = parseUpdate( fields, timeByMethod );
                        int objId = rec.get_objId();
                        int fieldId = rec.get_fieldId();
                        ObjectModel obj = heap.get(objId);

                        //Ignore static vars
                        if(objId == 0) continue;

                        //Object alloc record does not exist, so we make one
                        //To signify this, the object has type ""
                        //TODO: Maybe replace this type with java/lang/Object
                        if(obj == null){
                            obj = new ObjectModel(objId, "", timeByMethod);
                            heap.put(objId, obj);
                        }

                        if(obj.hasField(fieldId)){
                            ObjectModel.FieldData field = obj.getField(fieldId);

                            //Process data as a fact
                            program += rulegen(objId, field.get_objId(), field.get_creationTime(), timeByMethod, db_interface);
                        }

                        //Don't add a null object as a target here
                        //Represent it as a missing pointer instead
                        if(rec.get_newTgtId() == 0) continue;

                        obj.addField(fieldId, rec.get_timeByMethod(), rec.get_newTgtId());

                    } else if(isDeath(fields[0])) {
                        DeathRecord rec = parseDeath( fields, timeByMethod );
                        int objId = rec.get_objId();
                        ObjectModel obj = heap.get(objId);

                        if(objId == 0) continue;

                        //This death has no corresponding allocation.
                        //We can ignore it since it will have no fields either
                        if(obj == null){
                            continue;
                        }
                        //Process dead fields
                        for (ObjectModel.FieldData field : obj.getFields()){
                            program += rulegen(objId, field.get_objId(), field.get_creationTime(), timeByMethod, db_interface);
                        }
                        insertObject( objId,
                                      obj.get_type(),
                                      obj.get_allocTime(),
                                      timeByMethod,
                                      db_interface );
                        heap.remove(objId);
                    }

                    i += 1;
                    if (i % 10000 == 1) {
                        System.out.print(".");
                    } 

                    if(i == 100000) break;
                }

                timeByMethod++;

                //process immortals
                //System.err.println("Processing immortals");
                for( ObjectModel obj : heap.values() ){
                    // Insert Immortals into DB.
                    for( ObjectModel.FieldData field : obj.getFields() ){
                        program += rulegen(obj.get_objId(), field.get_objId(), field.get_creationTime(), timeByMethod, db_interface);
                    }
                    insertObject( obj.get_objId(),
                                  obj.get_type(),
                                  obj.get_allocTime(),
                                  timeByMethod,
                                  db_interface );
                }

                program += timestampRule(timeByMethod);
                }


            //System.out.println(program);
            System.out.println("\n");
        } catch (IOException e) {
            System.err.println( e.getClass().getName() + ": " + e.getMessage() );
            System.exit(0);
        }

        return program;
    }

    private static String rulegen(int from_id,
                                  int to_id,
                                  int startTime,
                                  int endTime,
                                  DBInterface db_interface) throws SQLException {
        String obj_id = "'" + "A" + from_id + "'";
        String tgt_id = "'" + "A" + to_id + "'";
        String fact = "pointsTo(" + obj_id + "," + tgt_id + "," + startTime + "," + endTime + ")" + ".";

        db_interface.insertPointer(from_id, to_id, startTime, endTime);
        //System.err.println(fact);

        return fact + "\n";
        /*
           try{
           p.parse(fact);
           } catch (ParserException e){
           System.err.println( e.getClass().getName() + ": " + e.getMessage() );
           System.exit(0);
           }
           */
    }

    private static void insertObject( int objId,
                                      String type,
                                      int allocTime,
                                      int deathTime,
                                      DBInterface db_interface) throws SQLException {
        db_interface.insertObject(objId, type, allocTime, deathTime);
    }

    private static String timestampRule(int endTime){
        String instantRule = "pointsToInstant(?A,?B,?T) :- timestamp(?T), pointsTo(?A,?B,?S,?E), ?T >= ?S, ?E > ?T" + ".";
        String timestampBaseRule = "timestamp(0)" + ".";
        String timestampIndRule = "timestamp(?t) :- ?s + 1 = ?t, timestamp(?s), ?t <= " + endTime + ".";

        //System.err.println(instantRule);
        //System.err.println(timestampBaseRule);
        //System.err.println(timestampIndRule);


        return instantRule + "\n" + timestampBaseRule + "\n" + timestampIndRule + "\n";
        /*
           try{
           p.parse(instantRule);
           p.parse(timestampBaseRule);
           p.parse(timestampIndRule);
           } catch (ParserException e){
           System.err.println( e.getClass().getName() + ": " + e.getMessage() );
           System.exit(0);
           }
           */
    }


    private static boolean isUpdate(String op) {
        return op.equals("U");
    }

    private static boolean isAllocation( String op ) {
        return (op.equals("A") || op.equals("N") || op.equals("P") || op.equals("I"));
    }

    private static boolean isDeath(String op) {
        return op.equals("D");
    }

    private static ObjectRecord parseAllocation( String[] fields, int timeByMethod ) {
        // System.out.println("[" + fields[0] + "]");
        int objId = Integer.parseInt( fields[1], 16 );
        String type = fields[3];
        // UNUSED right now:
        // int size = Integer.parseInt( fields[2], 16 );
        // int site = Integer.parseInt( fields[4], 16 );
        // int length = Integer.parseInt( fields[5], 16 );
        // int threadId = Integer.parseInt( fields[6], 16 );
        return new ObjectRecord( 0, // Autogenerated by database
                objId,
                0, // Unknown at this point
                timeByMethod,
                0, // Unknown at this point
                type );
    }

    private static UpdateRecord parseUpdate( String[] fields, int timeByMethod ) {
        int oldTgtId = Integer.parseInt( fields[1], 16 );
        int objId = Integer.parseInt( fields[2], 16 );
        int newTgtId = Integer.parseInt( fields[3], 16 );
        int fieldId = 0;
        try {
            fieldId = Integer.parseInt( fields[4], 16 );
        }
        catch ( Exception e ) {
            try {
                System.out.println( String.format("parseInt failed: %d -> %s", objId, fields[4]) );
                BigInteger tmp = new BigInteger( fields[4], 16 );
                fieldId = tmp.intValue();
            }
            catch ( Exception e2 ) {
                System.err.println( e2.getClass().getName() + ": " + e2.getMessage() );
                System.exit(0);
            }
        }

        int threadId = Integer.parseInt( fields[5], 16 );
        return new UpdateRecord( objId,
                oldTgtId,
                newTgtId,
                fieldId,
                threadId,
                timeByMethod );
    }

    private static DeathRecord parseDeath( String [] fields, int timeByMethod ){
        int objId = Integer.parseInt(fields[0], 16);
        return new DeathRecord(objId);
    }
}
