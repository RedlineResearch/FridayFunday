package net.veroy.analysis;

import java.util.HashMap;
import java.util.Collection;

public class ObjectModel {
    private int _objId;
    private String _type;
    private HashMap<Integer, FieldData> fields;

    public ObjectModel(int objId, String type){
        this._objId = objId;
        this._type = type;
        fields = new HashMap<Integer, FieldData>();
    }

    public void addField(int fieldId, int creationTime, int targetId){
        fields.put(fieldId, new FieldData(creationTime, targetId));
    }

    public FieldData getField(int fieldId){
        return fields.get(fieldId);
    }

    public boolean hasField(int fieldId){
        return fields.containsKey(fieldId);
    }

    public Collection<FieldData> getFields(){
        return fields.values();
    }

    public int get_objId(){
        return _objId;
    }


    class FieldData {
        final int _creationTime;
        final int _objId;

        FieldData(int creationTime, int objId){
            this._creationTime = creationTime;
            this._objId = objId;
        }

        public int get_creationTime(){ return _creationTime; }
        public int get_objId(){ return _objId; }
    }
}
