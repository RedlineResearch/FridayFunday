TRACEFILE=$1

if [ -z $TRACEFILE ]
then
    echo "Missing trace file. Add **absolute** path to trace file."
    echo "Usage: run_iris.sh /absolute/path/to/trace"
elif [ ! -e $TRACEFILE ]
then
    echo "File referenced by ${TRACEFILE} does not exist"
    echo "Usage: run_iris.sh /absolute/path/to/trace"
else
    make all
    pushd ./src > /dev/null
    echo "Running program"
    # java -cp .:../lib/iris-0.60.jar:../lib/iris-app-0.60.jar:../lib/iris-parser-0.60.jar -Xms16G -Xmx64G -XX:-UseGCOverheadLimit net.veroy.analysis.IrisTest01 $TRACEFILE
    java -cp .:../lib/iris-0.60.jar:../lib/iris-app-0.60.jar:../lib/iris-parser-0.60.jar:../lib/sqlite-jdbc-3.8.11.1.jar -Xms16G -Xmx64G -XX:-UseGCOverheadLimit net.veroy.analysis.IrisTest01 $TRACEFILE
    popd > /dev/null
fi
