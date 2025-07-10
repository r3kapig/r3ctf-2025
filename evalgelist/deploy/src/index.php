<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evalgelist</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            background: white;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .output {
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        .error {
            color: #dc3545;
            font-weight: bold;
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .filtered {
            color: #6c757d;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Evalgelist - Try secure eval function</h1>
        
        <div class="warning">
            <strong>⚠️ Security Notice:</strong> This system uses advanced filtering to prevent malicious code execution. 
            Only safe PHP functions are allowed.
        </div>

        <form method="GET" action="">
            <div class="input-group">
                <label for="code">Enter PHP function name to validate:</label>
                <input type="text" id="code" name="input" placeholder="e.g., phpinfo, strlen, time">
            </div>
            <button type="submit">🔍 Validate Function</button>
        </form>

        <?php
        if (isset($_GET['input'])) {
            echo '<div class="output">';

            $filtered = str_replace(['$', '(', ')', '`', '"', "'", "+", ":", "/", "!", "?"], '', $_GET['input']);
            $cmd = $filtered . '();';
            
            echo '<strong>After Security Filtering:</strong> <span class="filtered">' . htmlspecialchars($cmd) . '</span>' . "\n\n";
            
            echo '<strong>Execution Result:</strong>' . "\n";
            echo '<div style="border-left: 3px solid #007bff; padding-left: 15px; margin-left: 10px;">';
            
            try {
                ob_start();
                eval($cmd);
                $result = ob_get_clean();
                
                if (!empty($result)) {
                    echo '<span class="success">✅ Function executed successfully!</span>' . "\n";
                    echo htmlspecialchars($result);
                } else {
                    echo '<span class="success">✅ Function executed (no output)</span>';
                }
            } catch (Error $e) {
                echo '<span class="error">❌ Error: ' . htmlspecialchars($e->getMessage()) . '</span>';
            } catch (Exception $e) {
                echo '<span class="error">❌ Exception: ' . htmlspecialchars($e->getMessage()) . '</span>';
            }
            
            echo '</div>';
            echo '</div>';
        }
        ?>
</body>
</html>
