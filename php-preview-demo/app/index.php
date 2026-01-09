<?php
$host = getenv('DB_HOST') ?: 'db';
$db   = getenv('DB_NAME') ?: 'app';
$user = getenv('DB_USER') ?: 'app';
$pass = getenv('DB_PASS') ?: 'app';

echo "<h1>Preview Environment OK</h1>";

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
    $rows = $pdo->query("SELECT id, name FROM users ORDER BY id")->fetchAll(PDO::FETCH_ASSOC);

    echo "<p>DB rows:</p><ul>";
    foreach ($rows as $r) {
        $id = (int)$r['id'];
        $name = htmlspecialchars($r['name']);
        echo "<li>{$id}: {$name}</li>";
    }
    echo "</ul>";
} catch (Throwable $e) {
    echo "<p><b>DB not ready yet</b> (refresh in a few seconds)</p>";
    echo "<pre>" . htmlspecialchars($e->getMessage()) . "</pre>";
}
