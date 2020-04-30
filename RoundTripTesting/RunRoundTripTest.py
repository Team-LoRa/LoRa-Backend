import os
import sys


def main():
    os.system( "kotlinc RoundTripTest.kt -cp json.jar LoraNodeConnection.kt -include-runtime -d RoundTripTest.jar" )
    os.system( "java -cp RoundTripTest.jar:json.jar:LoraNodeConnection.kt RoundTripTestKt" )

    os.system( "python3 RoundTripTest.py" )



if __name__ == "__main__":
    sys.exit(main())
