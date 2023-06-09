<?php
    include_once('esp-database.php');

    $action = $id = $name = $gpio = $state = "";

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $action = test_input($_POST["action"]);
        if ($action == "output_delay") {
            $delay = test_input($_POST["delay"]);
            $result = setDelay($delay);
            echo $result;
        }
		else if ($action == "output_create") {
            $name = test_input($_POST["name"]);
            $gpio = test_input($_POST["gpio"]);
            $state = test_input($_POST["state"]);
            $result = createOutput($name, $gpio, $state);
            echo $result;
        }
        else {
            echo "No data posted with HTTP POST.";
        }
    }

    if ($_SERVER["REQUEST_METHOD"] == "GET") {
        $action = test_input($_GET["action"]);
        if ($action == "outputs_state") {
            $result = getAllOutputStates();
            if ($result) {
                while ($row = $result->fetch_assoc()) {
                    $rows[$row["gpio"]] = $row["state"];
                }
            }
			$delayTime = getDelay();
            if ($delayTime) {
                while ($row = $delayTime->fetch_assoc()) {
                    $delay = $row["Value"];
                }
            }
			$all = array("Delay"=>$delay, "Main"=>$rows);
			
            echo json_encode($all);
        }
        else if ($action == "output_update") {
            $id = test_input($_GET["id"]);
            $state = test_input($_GET["state"]);
            $result = updateOutput($id, $state);
            echo $result;
        }
        else if ($action == "output_delete") {
            $id = test_input($_GET["id"]);
            $result = deleteOutput($id);
            $result2 = getAllOutputStates();
            echo $result;
        }
        else {
            echo "Invalid HTTP request.";
        }
    }

    function test_input($data) {
        $data = trim($data);
        $data = stripslashes($data);
        $data = htmlspecialchars($data);
        return $data;
    }
?>