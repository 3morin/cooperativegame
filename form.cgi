#!/usr/bin/ruby -w
require "mylib"

#[1, 2] => v({1,2})
def coalition(arr)
   return "v({" + arr.sort.join(", ") + "})"
end

print <<"EOT"
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<title>協力ゲーム分析君</title>
<link rel="stylesheet" href="./css/form_result_style.css" />
</head>
<body>
<div id="header">

<h1>協力ゲーム分析君</h1>

<p id="tagline">--シャープレイ値の計算など--</p>

</div><!-- #header -->

<h2>提携値を入力してください</h2>

<p>
<span class="caution">※半角数字で全ての欄に入力</span>
</p>

<form action="result.cgi" method="POST">
<p>
EOT

cgi = CGI.new
n = cgi["number"].to_i
narr = (1..n).to_a
(1..n).each do |i|
   arr = narr.combinationN(i)
   arr.sort.each do |j|
      coalition_v = coalition(j)
      print "#{coalition_v} = <input type='text' name='v#{j}' value='' size='5'><br>"
   end
end

filename = "#{new_id()}"

print <<"EOT"
</p>
<p>
<input type="hidden" name="number" value="#{n}">
<input type="hidden" name="filename" value="#{filename}">
<input type="submit" value="分析する">
</p>
</form>
</body>
</html>
EOT