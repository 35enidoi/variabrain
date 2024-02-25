import time
from shutil import get_terminal_size
from variabrain.exceptions import *

def interpreter(code:str,*,
          # ここはインタプリンタの設定関連
          speinp:str=None,
          retmode:bool=False,
          yiemode:bool=False,
          # ここはbrainfuckの設定関係
          sizebit:int=8,
          sizemem:int=0,
          tooinc:bool=False,
          toodec:bool=False,
          # ここから下はdebag関係
          debug:bool=False,
          ret16:bool=False,
          log:bool=False,
          stepmode:bool=False,
          steptime:int=0):
    # variabrainインタプリンタによって予約している文字たち
    __SYSTEM_RESERVE_CHAR = ("[", "]", ">", "<", "+", "-", ",", ".", "(", ")")

    coded = tuple(code.strip())
    if sizemem > 0:
        point = [0 for _ in range(sizemem)]
    else:
        point = [0]
    if stepmode:
        output = ""
    if log:
        logs = ""
    if speinp is not None:
        specialinputs = list(speinp)
    if retmode and yiemode:
        yiemode  = False
    if retmode:
        returns = ""
    if yiemode:
        yieldlist = []
    nowpoint = 0
    n = 0
    bit = (2**sizebit)-1
    step = 0

    def bracket_searcher(bracketslike:list[tuple[str, int]], n_:int) -> int:
        "bracketの探索する奴"
        nowchar = coded[n_]
        index = bracketslike.index((nowchar, n_))
        balance = 1

        while balance != 0:
            index += 1
            if bracketslike[index][0] == nowchar:
                balance += 1
            else:
                balance -= 1

        return bracketslike[index][1]

    def static_bracket_analysis(bracketslike:list[tuple[str, int]], openb:str, closeb:str) -> None:
        if len(bracketslike) != 0:
            # まずブラケットがあるコードなのか(index out of range対策)
            if (openb_c := (brlist := tuple(map(lambda x:str(x[0]), bracketslike))).count(openb)) != (closeb_c := brlist.count(closeb)):
                # openbとclosebの量が違う
                if openb_c-closeb_c > 0:
                    # closebの量が多い
                    raise CloseBracketError(f"too many `{closeb}`.")
                else:
                    # openbの量が多い
                    raise OpenBracketError(f"too many `{closeb}`.")
            elif brlist[0] == closeb:
                # 初めに閉じるブラケットのある無効なプログラムである
                raise CloseBracketError(f"first character is `{closeb}`.")
            else:
                # []][[]みたいなブラケットが向かい合ってないコードを弾く部分
                barance = 0
                for i in brlist:
                    if i == openb:
                        barance += 1
                    else:
                        barance -= 1
                        if barance < 0:
                            # openbとclosebが向かい合っていないため、実行できない
                            raise BracketError(f"brackets `{openb}` and `{closeb}` do not match.")

    # 角括弧のリスト
    brackets = [(i, v) for v, i in enumerate(coded) if i == "[" or i == "]"]
    # 角括弧の静的解析
    static_bracket_analysis(brackets, "[", "]")
    # [に対応する]の辞書
    bracketpos = {v: bracket_searcher(brackets, v) for v in (i[1] for i in brackets if i[0] == "[")}
    # ]に対応する[の辞書
    rbracketpos = {v:i for i, v in bracketpos.items()}

    # ここからvariabrainのvariableの変数
    # 変数のリスト
    variables = {}
    # 移動した場所を記憶するバッファ
    buffer = []
    # 丸括弧のリスト
    circlebrackets = [(i, v) for v, i in enumerate(coded) if i == "(" or i == ")"]
    # 丸括弧の解析
    static_bracket_analysis(circlebrackets, "(", ")")
    # 角括弧と同様、(に対する)
    c_bracketpos = {v: bracket_searcher(circlebrackets, v) for v in (i[1] for i in circlebrackets if i[0] == "(")}
    # `(`の前が予約文字ではないか
    if any(((coded[i-1] in __SYSTEM_RESERVE_CHAR) for i in c_bracketpos)):
        raise BracketError("System reserved character do not locate on before `(`.")
    # (と)の間の角括弧のバランスが大丈夫か
    for i, v in c_bracketpos.items():
        balance = 0
        for r in coded[i:v]:
            if r == "[":
                balance += 1
            elif r == "]":
                balance -= 1
        if balance != 0:
            raise BracketError("`[]` balance invalid among `()`")

    if (stepmode or debug) and (not yiemode) and (not retmode):
        print("\n"+code.strip()+"\n")

    try:
        while n < len(coded):
            i = coded[n]
            if i == "]":
                if point[nowpoint] != 0:
                    n = rbracketpos[n]
            elif i == "[":
                if point[nowpoint] == 0:
                    n = bracketpos[n]
            elif i == ">":
                nowpoint += 1
                if len(point) == nowpoint:
                    if sizemem > 0:
                        if tooinc:
                            nowpoint = 0
                        else:
                            raise PointError("Pointer too increment")
                    else:
                        point.append(0)
            elif i == "<":
                nowpoint -= 1
                if nowpoint == -1:
                    if toodec:
                        nowpoint = len(point)-1
                    else:
                        raise PointError("Pointer too decrement")
            elif i == "+":
                if point[nowpoint] == bit:
                    point[nowpoint] = 0
                else:
                    point[nowpoint] += 1
            elif i == "-":
                point[nowpoint] -= 1
                if point[nowpoint] == -1:
                    point[nowpoint] = bit
            elif i == ".":
                returnchar = chr(point[nowpoint])
                if retmode:
                    returns += returnchar
                elif stepmode:
                    output += returnchar
                elif yiemode:
                    yieldlist.append({"output":returnchar})
                else:
                    print(returnchar,end="")
            elif i == ",":
                if speinp is not None:
                    if len(specialinputs) == 0:
                        # ASCIIでのEOFは調べた限り多分26
                        point[nowpoint] = 26
                        # 二回目に参照されたらエラー吐くようにする
                        specialinputs = None
                    elif specialinputs is None:
                        raise SpeinpTooGetError("too get inputs.")
                    point[nowpoint] = ord(specialinputs.pop(0))
                else:
                    point[nowpoint] = ord(list(input())[0])
            # ここから下variabrainの機能
            elif i == "(":
                # variabrainで`(`を直接実行することはない。
                # つまり、この説が実行されるのは完全におかしい。
                raise BrainException("`(` was detected.")
            elif i == ")":
                n = buffer.pop()
            else:
                # characterに当たった時
                if (num := c_bracketpos.get(n+1)) is not None:
                    # 定義
                    variables[i] = n+1
                    n = num
                elif (num := variables.get(i)):
                    # 定義済みの物
                    buffer.append(n)
                    n = num
                # 定義されてもなく、定義でもないものはコメントとして扱う。
            n += 1
            step += 1
            if log:
                logs += i
            if stepmode:
                if yiemode:
                    yieldlist.append({"codeat":n, "codein":i, "step":step, "nowpoint":nowpoint, "point":point, "output":output})
                    continue
                elif retmode:
                    continue
                passage = "codeat;{} codein;{} step;{} nowpoint;{} point;{} output;[{}]\r".format(n, i if i != "\n" else "", step, nowpoint, point, output)
                upnum = passage.count("\n")+len(passage)//get_terminal_size().columns
                print(passage+("\033[1A"*upnum),end="")
                time.sleep(steptime)
    except BrainException:
        raise
    finally:
        if retmode:
            return returns
        if yiemode:
            return yieldlist
        if n == 0:
            # なんもない、while分の中身実行してないので危ない。
            return
        if stepmode:
            # ターミナルで文字の入力の場所が変になってるので直す
            passage = f"codeat;{n} codein;{i} step;{step} nowpoint;{nowpoint} point;{point} output;[{output}]\r"
            downnum = passage.count("\n")+len(passage)//get_terminal_size().columns
            print("\n"*downnum)
        if debug:
            if stepmode:
                # stepmode時は変になるので改行一個なくす
                print("\n"+str(nowpoint))
            else:
                print("\n\n"+str(nowpoint))
            if ret16:
                print(list(map(lambda x: format(x,"02x"), point)))
            else:
                print(point)
            if log:
                print(logs)