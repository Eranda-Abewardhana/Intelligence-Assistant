<?php
    $servername = "localhost";
    $dbname = "id16364371_tsdb";
    $username = "id16364371_mynewdatabase";
    $password = "H2}V28vFkPlnrnZ2";
    
	if (isset($_COOKIE['cookie'])) {
		foreach ($_COOKIE['cookie'] as $name => $value) {
			$name = htmlspecialchars($name);
			$value = htmlspecialchars($value);
			global $user;
			if($name=='user'){
				$user = $value;
			}
		}
	}

    function createOutput($name, $gpio, $state) {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "INSERT INTO outputs (name, gpio, state)
        VALUES ('" . $name . "', '" . $gpio . "', '" . $state . "')";

        if ($conn->query($sql) === TRUE) {return "New output created successfully";}
        else {return "Error: " . $sql . "<br>" . $conn->error;}
        $conn->close();
    }

    function deleteOutput($id) {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "DELETE FROM outputs WHERE id='". $id .  "'";

        if ($conn->query($sql) === TRUE) {return "Output deleted successfully";}
        else {return "Error: " . $sql . "<br>" . $conn->error;}
        $conn->close();
    }

    function updateOutput($id, $state) {
        global $servername, $username, $password, $dbname, $user;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "UPDATE outputs SET state='" . $state . "' WHERE id='". $id .  "'";
        $EX2 = $conn->query($sql);
		
		$sql = "SELECT * FROM outputs WHERE id='". $id .  "'";
		$EX1 = $conn->query($sql);
		while ($row = $EX1->fetch_assoc()) {
			$gpio = $row['gpio'];
		}
		
		$sql = "DELETE FROM boards LIMIT 1;";
		$EX2 = $conn->query($sql);

		$sql = "INSERT INTO boards (User, gpio, State)
        VALUES ('" . $user . "', '" . $gpio . "', '" . $state . "');";
		
        if ($conn->query($sql) === TRUE) {return "Output History Inserted successfully";}
        else {return "Error: " . $sql . "<br>" . $conn->error;}
		
        $conn->close();
    }

    function getAllOutputs() {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "SELECT id, name, gpio, state FROM outputs";
        if ($result = $conn->query($sql)) {return $result;}
        else {return false;}
        $conn->close();
    }

    function getAllOutputStates() {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "SELECT gpio, state FROM outputs";
        if ($result = $conn->query($sql)) {
            return $result;
        }
        else {
            return false;
        }
        $conn->close();
    }
	
	function getHistory() {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "SELECT * FROM boards";
        if ($result = $conn->query($sql)) {return $result;}
        else {return false;}
        $conn->close();
    }
	
	function setDelay($delay) {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "UPDATE details SET Value='" . $delay . "' WHERE Data='SwitchDelay'";
        if ($result = $conn->query($sql)) {return $result;}
        else {return false;}
        $conn->close();
    }
	
	function getDelay() {
        global $servername, $username, $password, $dbname;

        $conn = new mysqli($servername, $username, $password, $dbname);
        if ($conn->connect_error) {die("Connection failed: " . $conn->connect_error);}

        $sql = "SELECT Value FROM details WHERE Data='SwitchDelay'";
        if ($result = $conn->query($sql)) {return $result;}
        else {return false;}
        $conn->close();
    }
	
?>