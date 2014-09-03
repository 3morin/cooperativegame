#!/usr/bin/ruby -w
require "mylib"
require "mathn"

def fact(n)
(1..n).to_a.inject(1){|r, i| r * i}
end

#「文字+数字」に対して数字のみをばらした配列を返す。v123 => [1,2,3]
def menbers(v)
   arr = v.split(//)
   arr.shift
   return arr
end

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

EOT

cgi = CGI.new

check = "ok"
cgi.keys.each do |i|
   if cgi[i] =~ /\D/ || cgi[i].empty? then
      check = "error"
      if cgi[i] =~ /\d.\d/ then#小数はok
         check = "ok"
      end
   end
end

if check == "error" then
   puts "<p id='error'>エラー：すべての欄に半角数字で入力してください</p>"
   puts "</body>", "</html>"
else

print <<"EOT"
<h2>分析完了</h2>
<ol>
EOT

n = cgi["number"].to_i

#x1~xnが送られたか
xi = "yes"
(1..n).each do |i|
   allocation = "x" + i.to_s
   if cgi[allocation].empty? then
      xi = "no"
   end
end

#vが送られていれば
if xi == "no" then

#提携値を配列に入れる
game_r = []
narr = (1..n).to_a
(1..n).each do |i|
   arr = narr.combinationN(i)
   arr.sort.each do |j|
      coalition1 = "v" + j.to_s
      coalition2 = coalition(j)
      game_r << "#{coalition2} = #{cgi[coalition1]}"
   end
end
game_r = game_r.join(", ")

#シャープレイ値を計算
shapleys = {}
sv = "("
(1..n).each do |k|
   i_sum = 0
   cgi.keys.each do |l|
      if l =~ /v/ and l =~ /#{k}/ then
         snumber = l.split(//).size - 1
         vs = cgi[l].to_f
         if snumber >= 2 then
            l_i = l.sub(/#{k}/, "")
            vs_i = cgi[l_i].to_f
         else
            vs_i = 0
         end
         a_element = (fact(snumber-1).to_f * fact(n-snumber).to_f / fact(n).to_f) * (vs - vs_i)
         i_sum += a_element
      end
   end
   shapleys[k] = i_sum
   sv += i_sum.to_s + ", "
end
sv.rstrip!
sv.chop!
sv += ")"
sv_r = "シャープレイ値 (φ_1, …, φ_#{n}) = #{sv}"

#シャープレイ値がコアに入っているか判定
s_core = "yes"
s_notcore = []
cgi.keys.each do |k|
   if k =~ /v/ and k =~ /\d/ then
      s_sum = 0
      s_arr = []
      core_menber = menbers(k)
      coalition_s = coalition(core_menber)
      core_menber.each do |l|
         l = l.to_i
         s_sum += shapleys[l]
         s_arr << "φ_" + l.to_s
      end
      if s_sum + 0.0001 < cgi[k].to_f then #40.0<40等を回避
         s_core = "not"
         if s_arr.length >= 2 then
            s_arr = s_arr.join("+")
         end
         s_notcore << "#{s_arr} = #{s_sum} &lt; #{coalition_s} = #{cgi[k]}"
      end
   end
end
s_notcore = s_notcore.sort{|a, b| a.size <=> b.size} #文字列で昇順ソート
s_notcore = s_notcore.join(", ")

if s_core == "yes" then
   core_r = "<span class='yescore'>コアに属する</span>"
   core_subr = ""
elsif s_core == "not" then
   core_r = "<span class='notcore'>コアに属さない</span>"
   core_subr = s_notcore
end

#凸ゲームか判定
convex = "yes"
notconvex = []
cgi.keys.each do |k|
   if  k =~ /v/ and k =~ /\d/ then
      convex_m1 = menbers(k)
      coalition_m1 = coalition(convex_m1)
      cgi.keys.each do |l|
         if l =~ /\d/ then
            convex_m2 = menbers(l)
            coalition_m2 = coalition(convex_m2)
            orset = convex_m1 | convex_m2 
            andset = convex_m1 & convex_m2
            orvalue = "v" + orset.sort.join
            andvalue = "v" + andset.sort.join
            orcoaliton = coalition(orset)
            andcoalition = coalition(andset)
            if andvalue =~ /^v$/ then
               if cgi[k].to_f + cgi[l].to_f > cgi[orvalue].to_f then
                  convex = "not"
                  if k < l then
                     notconvex << "#{coalition_m1} + #{coalition_m2} &gt; #{orcoaliton}"
                  else
                     notconvex << "#{coalition_m2} + #{coalition_m1} &gt; #{orcoaliton}"
                  end
               end
            else
               if cgi[k].to_f + cgi[l].to_f > cgi[orvalue].to_f + cgi[andvalue].to_f then
               convex = "not"
                  if k < l then
                     notconvex << "#{coalition_m1} + #{coalition_m2} &gt; #{orcoaliton} + #{andcoalition}"
                  else
                     notconvex << "#{coalition_m2} + #{coalition_m1} &gt; #{orcoaliton} + #{andcoalition}"
                  end
               end
            end
         end
      end
   end
end
notconvex = notconvex.uniq.sort
notconvex = notconvex.join(", ")

if convex == "yes" then
  convex_r = "<span class='yesconvex'>凸ゲーム</span>"
  convex_subr = ""
else
  convex_r = "<span class='notconvex'>凸ゲームでない</span>"
  convex_subr = notconvex
end

filename = cgi["filename"]
File.open("./text/#{filename}.txt", "a") do |fh|

# game_r, sv_r, core_r, core_subr, convex_r, convex_subr
fh.print <<"EOT"
  <li class="a_game"><span class="game">#{game_r}</span>
    <ul class="analisis">
      <li class="convex"><span class="convex_r">#{convex_r}</span>
EOT
fh.puts "<ul><li class='convex_subr'>#{convex_subr}</li></ul>" if convex_subr.empty? == false
fh.print <<"EOT"
      </li>
      <li class="shapley"><span class="sv">#{sv_r}</span>
        <ul>
          <li class="core"><span class="core_r">#{core_r}</span>
EOT
     fh.puts "<ul><li class='core_subr'>#{core_subr}</li></ul>" if core_subr.empty? == false
fh.print <<"EOT"
          </li>
        </ul>
      </li>
    </ul>
  </li>
EOT
#fileclose
end
#if xi == "no" then
end

#xが送られた時
if xi == "yes" then

#ファイルの末尾から3行消去
filename = cgi["filename"]
#ファイルの行数取得
fh1 = File.open("./text/#{filename}.txt", "r")
linenumber = 0
while line = fh1.gets do
   linenumber += 1
end
fh1.close

fh2 = File.open("./text/#{filename}.txt", "r")
buffer = "buffer-#{new_id()}"
fh3 = File.open("./text/#{buffer}.txt", "w")
linecount = 0
while line = fh2.gets do
   linecount += 1
   if linecount <= linenumber -3 then
      fh3.puts line
   end
end
fh3.close
fh2.close

File.open("./text/#{filename}.txt", "w") do |fh|
   File.open("./text/#{buffer}.txt", "r") do |buffer|
     fh.puts buffer.read
   end
end

#配分を変数に格納、配分かどうか調べる
alloarr = []
an_sum = 0
cgi.keys.sort.each do |i|
   if i =~ /x/ then
      alloarr << cgi[i]
      an_sum += cgi[i].to_f
   end
end
#v全体提携を作る
wholev = ["v"]
(1..n).each do |i|
   wholev << i.to_s
end
wholev = wholev.join("")
allos = "(" + alloarr.join(", ") + ")"
#個人合理性を満たすか
indi_ratio = "yes"
indi_ratio_not = []
(1..n).each do |i|
   vnum = "v" + i.to_s
   xnum = "x" + i.to_s
   if cgi[xnum].to_f < cgi[vnum].to_f then
      indi_ratio = "no"
      indi_ratio_not << "x_#{i} &lt; v({#{i}})"
   end
end
#全体合理性and個人合理性を満たしていれば
if an_sum == cgi[wholev].to_f and indi_ratio == "yes" then
   allo_r = "配分 (x_1, …, x_#{n}) = #{allos}"

#ある配分がコアに属するか
x_core = "yes"
x_notcore = []
cgi.keys.each do |k|
   if k =~ /v/ and k =~ /\d/ then
      x_sum = 0
      x_arr = []
      x_core_menber = menbers(k)
      coalition_x = coalition(x_core_menber)
      x_core_menber.each do |l|
         allocation = "x" + l.to_s
         x_sum += cgi[allocation].to_f
         x_arr << "x_" + l.to_s
      end
      if x_sum + 0.0001 < cgi[k].to_f then #40.0<40等を回避
         x_core = "not"
         if x_arr.length >= 2 then
            x_arr = x_arr.join("+")
         end
         x_notcore << "#{x_arr} = #{x_sum} &lt; #{coalition_x} = #{cgi[k]}"
      end
   end
end
x_notcore = x_notcore.sort{|a, b| a.size <=> b.size} #文字列で昇順ソート
x_notcore = x_notcore.join(", ")

if x_core == "yes" then
   x_core_r = "<span class='yescore'>コアに属する</span>"
   x_core_subr = ""
elsif x_core == "not" then
   x_core_r = "<span class='notcore'>コアに属さない</span>"
   x_core_subr = x_notcore
end

#全体合理性のみ満たさなければ
elsif an_sum != cgi[wholev].to_f and indi_ratio == "yes" then
   allo_r = "<span class='noteallo'>(x_1, …, x_#{n}) = #{allos} は配分ではありません</span>"
   x_core_r = "全体合理性 (x_1 + … +  x_#{n} = #{cgi[wholev]}) を満たしてください"
   x_core_subr = ""
#個人合理性のみ満たさなければ
elsif an_sum == cgi[wholev].to_f and indi_ratio == "no" then
   allo_r = "<span class='noteallo'>(x_1, …, x_#{n}) = #{allos} は配分ではありません</span>"
   x_core_r = "個人合理性 (x_i &gt;= v({i}) for all i) を満たしてください"
   x_core_subr = indi_ratio_not.join(", ")
#全体合理性も個人合理性も満たさなければ
elsif an_sum != cgi[wholev].to_f and indi_ratio == "no" then
   allo_r = "<span class='noteallo'>(x_1, …, x_#{n}) = #{allos} は配分ではありません</span>"
   x_core_r1 = "全体合理性 (x_1 + … +  x_#{n} = #{cgi[wholev]}) を満たしてください"
   x_core_r2 = "個人合理性 (x_i &gt;= v({i}) for all i) を満たしてください"
   x_core_subr = indi_ratio_not.join(", ")
end

if an_sum != cgi[wholev].to_f and indi_ratio == "no" then
#ファイルへ書き込み
File.open("./text/#{filename}.txt", "a") do |fh|
   fh.print <<"EOT"
      <li class="allocation"><span class="allo_r">#{allo_r}</span>
        <ul>
          <li class='notratio'><span class='core_r'>#{x_core_r1}</span></li>
          <li class='notratio'><span class='core_r'>#{x_core_r2}</span>
EOT
   fh.puts "<ul><li class='core_subr'>#{x_core_subr}</li></ul>" if x_core_subr.empty? == false
   fh.puts "</li>", "</ul>", "</li>", "</ul>", "</li>"
end
else
#ファイルへ書き込み
File.open("./text/#{filename}.txt", "a") do |fh|
   fh.print <<"EOT"
      <li class="allocation"><span class="allo_r">#{allo_r}</span>
        <ul>
          <li class='notratio'><span class='core_r'>#{x_core_r}</span>
EOT
   fh.puts "<ul><li class='core_subr'>#{x_core_subr}</li></ul>" if x_core_subr.empty? == false
   fh.puts "</li>", "</ul>", "</li>", "</ul>", "</li>"
end
end
end

File.open("./text/#{filename}.txt", "r") do |rfh|
   print rfh.read
end

print <<"EOT"
</ol>
<form id="alloform" action="result.cgi" method="POST">
<p id="allop"><span class="alloexp">※ </span>このゲームのある配分がコアに属するかチェックする：
EOT

form = []
(1..n).each do |i|
   form << "x_#{i} = <input type='text' name='x#{i}' value='' size='5'>"
end

puts form.join(" "), "<input type='submit' value='チェック'>"

print <<"EOT"
</p>
<p id="allohidden">
<input type="hidden" name="number" value="#{n}">
<input type="hidden" name="filename" value="#{filename}">
EOT
narr = (1..n).to_a
(1..n).each do |i|
	arr = narr.combinationN(i)
	arr.sort.each do |j|
           vj = "v" + "#{j}"
		puts "<input type='hidden' name='v#{j}' value='#{cgi[vj]}'>"
	end
end
print <<"EOT"
</p>
</form>

<div id="another">
<h2>続けて他のゲームを分析する</h2>
<p class="anotherexp">提携値を入力してください。</p>
<form action="result.cgi" method="POST">
<p>
EOT

narr = (1..n).to_a
(1..n).each do |i|
   arr = narr.combinationN(i)
   arr.sort.each do |j|
      coalition_v = coalition(j)
      print "#{coalition_v} = <input type='text' name='v#{j}' value='' size='5'><br>"
   end
end

print <<"EOT"
</p>
<p>
<input type="hidden" name="number" value="#{n}">
<input type="hidden" name="filename" value="#{filename}">
<input type="submit" value="分析する">
</p>
</form>

<h2>プレイヤーの数を再選択する（トップページに戻る）</h2>
<p class="anotherexp">
<a href="./top.html">トップページに戻る</a><span id="caution">※今までの分析結果はリセットされます。</span>
</p>

</div><!-- #another -->
</body>
</html>
EOT
end