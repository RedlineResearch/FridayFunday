package net.veroy.analysis;


public class UpdateRecord {
    private int _objId;
    private int _oldTgtId;
    private int _newTgtId;
    private int _fieldId;
    private int _threadId;
    private int _timeByMethod;

    public UpdateRecord( int objId,
                         int oldTgtId,
                         int newTgtId,
                         int fieldId,
                         int threadId,
                         int timeByMethod) {
        super();
        this._objId = objId;
        this._oldTgtId = oldTgtId;
        this._newTgtId = newTgtId;
        this._fieldId = fieldId;
        this._threadId = threadId;
        this.set_timeByMethod(timeByMethod);
    }

    public UpdateRecord() {
        super();
        this._objId = 0;
        this._oldTgtId = 0;
        this._newTgtId = 0;
        this._fieldId = 0;
        this._threadId = 0;
    }

    public int get_oldTgtId() {
        return _oldTgtId;
    }
    public void set_oldTgtId(int oldTgtId) {
        this._oldTgtId = oldTgtId;
    }
    public int get_objId() {
        return _objId;
    }
    public void set_objId(int objId) {
        this._objId = objId;
    }
    public int get_newTgtId() {
        return _newTgtId;
    }
    public void set_newTgtId(int newTgtId) {
        this._newTgtId = newTgtId;
    }
    public int get_fieldId() {
        return _fieldId;
    }
    public void set_fieldId(int fieldId) {
        this._fieldId = fieldId;
    }
    public int get_threadId() {
        return _threadId;
    }
    public void set_threadId(int threadId) {
        this._threadId = threadId;
    }
    public int get_timeByMethod() {
        return _timeByMethod;
    }
    public void set_timeByMethod(int timeByMethod) {
        this._timeByMethod = timeByMethod;
    }
}
