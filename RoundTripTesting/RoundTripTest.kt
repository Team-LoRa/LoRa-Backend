import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import com.teamlora.loralibrary.LoRaMessenger

fun main(args: Array<String>) {

    // Create output array
    val output = JSONArray()

    // Read the input file
    var jsonString: String = File("round_trip_input.json").readText(Charsets.UTF_8)

    // Convert it to an array
    val input = JSONArray( jsonString )

    // Iterate through the inputs
    for( i in 0 until input.length() ) {

        var inputTable : JSONObject = input.getJSONObject( i )

        // Read the other inputs from the input table
        val appName : String = inputTable.getString("app")
        val apiName : String = inputTable.getString("api")
        val paramsJSON : JSONArray = inputTable.getJSONArray("params")
        val encodingTableJSONString : String = File( inputTable.getString("encoding") ).readText(Charsets.UTF_8)

        // Create a messenger
        val messenger = LoRaMessenger( appName, encodingTableJSONString )

        // Convert the JSONArray into a traditional array
        var parameters = arrayOf<Any>()
        for( i in 0 until paramsJSON.length() ) {
          parameters += paramsJSON.get( i )
        }

        // Pass the parameters for encoding and add the resulting byte array to the output
        var encodedMessage : ByteArray = messenger.encodeMessage( apiName, parameters )

        // Convert the encoded message to unsigned bytes first, as that seems to be
        // what sending them over the socket does and is what the proxy server is
        // expecting
        // Also, have to then convert the unsigned bytes to integers because
        // Kotlin's JSONArray doesn't support unsigned bytes
        var outputMessage : IntArray = IntArray( 0 )

        for( byte in encodedMessage ) {
          outputMessage += byte.toUByte().toInt()
        }

        // Finally add the result to the output
        output.put( outputMessage )
    }

    // Write the all the results to a file
    File("encoding_output.json").writeText( output.toString() )

}
