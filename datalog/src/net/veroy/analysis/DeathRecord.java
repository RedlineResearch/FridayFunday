package net.veroy.analysis;

public class DeathRecord {
    private int _objId;

    public DeathRecord( int objId ){
        this._objId = objId;
    }

    public int get_objId() {
        return _objId;
    }

    public void set_objId(int objId){
        this._objId = objId;
    }
}
