<?php
if (isset($_COOKIE['cookie'])) {
	foreach ($_COOKIE['cookie'] as $name => $value) {
		$name = htmlspecialchars($name);
		$value = htmlspecialchars($value);
		
		if($name=='pass' and $value=='admin'){
			echo "<script>location.replace('admin.php');</Script>";
		}
		if($name=='pass' and $value==''){
			echo "<script>location.replace('user.php');</Script>";
		}
	}
} else {
	if (isset($_POST['login']) ) {
		$useName= $_POST['UseName'];
		$pss= $_POST['pass'];
		if($pss=='admin'){
			/* time()+(60*60*24*30) */
			setcookie("cookie[user]", $useName, time()+(60*60*24*30*360));
			setcookie("cookie[pass]", "admin", time()+(60*60*24*30*360));
			echo "<script>location.replace('admin.php');</Script>";
		} else {
			setcookie("cookie[user]", $useName, time()+(60*60*24*30*360));
			setcookie("cookie[pass]", "", time()+(60*60*24*30*360));
			echo "<script>location.replace('user.php');</Script>";
		}
	} else {
		echo "<script>location.replace('login.html');</Script>";
	}
}
?>