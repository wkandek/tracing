#
# demo service that calulates simple arithmetic expressions
# example: 2+3 (2+3)*7 etc
#

# use the built-in webserver for simplicity
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import html
# time to measure runtime of a request
import time
import os
import psutil
# the modules used to implment the gramamr
import ply.yacc as yacc
import ply.lex as lex

# version number
global version
version = "0.2"
global testmode
testmode = "OFF"

# web server config
hostName = "0.0.0.0"
serverPort = 8080

# statistics variables for metrics
wellformed = 0
wellformed_post = 0
nonwellformed = 0
starttime = 0
duration_bucket = {}

duration_bucket["1"] = 0
duration_bucket["2"] = 0
duration_bucket["4"] = 0
duration_bucket["8"] = 0
duration_bucket["16"] = 0
duration_bucket["32"] = 0
duration_bucket["32+"] = 0

# maximum input length
MAXLEN = 50

# calculater parser
tokens = (
    'NAME',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUALS',
    'LPAREN',
    'RPAREN',
)

# Tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'


# parser routines
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lex.lex()

# Precedence rules for the arithmetic operators
precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names (for storing variables)
names = { }

def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    names[p[1]] = p[3]

def p_statement_expr(p):
    'statement : expression'
    global wellformed
    p[0] = p[1]
    wellformed = wellformed + 1

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    try:
        if p[2] == '+'  : p[0] = p[1] + p[3]
        elif p[2] == '-': p[0] = p[1] - p[3]
        elif p[2] == '*': p[0] = p[1] * p[3]
        elif p[2] == '/': p[0] = p[1] / p[3]
    except:
        # for divide by 0
        pass

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = -p[2]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_name(p):
    'expression : NAME'
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0

def p_error(p):
    print("Syntax error at '%s'" % p.value)
    global nonwellformed
    nonwellformed = nonwellformed + 1


def write_form(self,operation,result):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Calc</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    # escape the operation which is the input string to assure printable text
    self.wfile.write(bytes(str(html.escape(operation)), "utf-8"))
    self.wfile.write(bytes(" = ", "utf-8"))
    self.wfile.write(bytes(str(result), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("<form action='parse' method='post'><input name='tocalc' type='text'><br><input type='submit'></form>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))


def write_metrics(self):
    self.send_response(200)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    #self.wfile.write(bytes("calc_{version=", "utf-8"))
    #self.wfile.write(bytes(str(version), "utf-8"))
    #self.wfile.write(bytes("} 1\n", "utf-8"))
    #self.wfile.write(bytes("test_mode ", "utf-8"))
    #self.wfile.write(bytes(str(testmode), "utf-8"))
    #self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("start_time ", "utf-8"))
    self.wfile.write(bytes(str(starttime), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("wellformed_total{method=\"get\"} ", "utf-8"))
    self.wfile.write(bytes(str(wellformed), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("wellformed_total{method=\"post\"} ", "utf-8"))
    self.wfile.write(bytes(str(wellformed_post), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("nonwellformed_total ", "utf-8"))
    self.wfile.write(bytes(str(nonwellformed), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    process = psutil.Process(os.getpid())
    self.wfile.write(bytes("memory ", "utf-8"))
    self.wfile.write(bytes(str(process.memory_info().rss), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"1\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["1"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"2\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["2"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"4\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["4"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"8\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["8"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"16\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["16"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"32\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["32"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))
    self.wfile.write(bytes("duration_bucket{le=\"32+\"} ", "utf-8"))
    self.wfile.write(bytes(str(duration_bucket["32+"]), "utf-8"))
    self.wfile.write(bytes("\n", "utf-8"))

def write_healthz(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>healthz</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("CalcVersion=", "utf-8"))
    self.wfile.write(bytes(str(version), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("testmode=", "utf-8"))
    self.wfile.write(bytes(str(testmode), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("wellformed=", "utf-8"))
    self.wfile.write(bytes(str(wellformed), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("nonwellformed=", "utf-8"))
    self.wfile.write(bytes(str(nonwellformed), "utf-8"))
    self.wfile.write(bytes("<br>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))


def fill_duration_bucket(duration):
    if duration < 0.0001:
        duration_bucket["1"] = duration_bucket["1"] + 1
    elif duration < 0.0002:
        duration_bucket["2"] = duration_bucket["2"] + 1
    elif duration < 0.0004:
        duration_bucket["4"] = duration_bucket["4"] + 1
    elif duration < 0.0008:
        duration_bucket["8"] = duration_bucket["8"] + 1
    elif duration < 0.0016:
        duration_bucket["16"] = duration_bucket["16"] + 1
    elif duration < 0.0032:
        duration_bucket["32"] = duration_bucket["32"] + 1
    else:
        duration_bucket["32+"] = duration_bucket["32+"] + 1


class CalcServer(BaseHTTPRequestHandler):

    def do_GET(self):
        start = time.time()
        # react to health checks, everything else is a request for a form
        if "/healthz" == self.path[0:8]:
            write_healthz(self)
        elif "/metrics" == self.path[0:8]:
            write_metrics(self)
        elif "/api" == self.path[0:4]:
            logstr = self.path[5:]
            # strings that are too long won be processed
            if len(logstr) > MAXLEN:
                self.send_response(414)
                self.end_headers()
            else:
                ulogstr = unquote(logstr)
                if "=" in ulogstr:
                    operation = ulogstr.split("=",1)[1]
                else:
                    operation = ulogstr
                result = parser.parse(operation)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                outstr = "{"+"\"operation\":\"{}\",\"result\":\"{}\"".format(html.escape(operation),result)+"}"
                self.wfile.write(bytes(str(outstr), "utf-8"))
        else:
            if testmode and testmode.upper() == "ON":
                write_form(self,"","")
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()

        if "/healthz" != self.path[0:8] and "/metrics" != self.path[0:8]:
           fill_duration_bucket(time.time() - start)


    def do_POST(self):
        global wellformed_post
        start = time.time()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if self.path == "/api":
            logstr = "{0}".format(post_data.decode('utf-8'))
            if len(logstr) > MAXLEN:
                self.send_response(414)
                self.end_headers()
            else:
                ulogstr = unquote(logstr)
                if "=" in ulogstr:
                    operation = ulogstr.split("=",1)[1]
                else:
                    operation = ulogstr
                result = parser.parse(operation)
                outstr = "{"+"\"operation\":\"{}\",\"result\":\"{}\"".format(operation,result)+"}"
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(bytes(str(outstr), "utf-8"))
                wellformed_post = wellformed_post + 1
        else:
            if testmode and testmode.upper() == "ON":
                logstr = "Body:\n{0}\n".format(post_data.decode('utf-8'))
                if len(logstr) > MAXLEN:
                    self.send_response(414)
                else:
                    ulogstr = unquote(logstr)
                    operation = ulogstr.split("=",1)[1]
                    result = parser.parse(operation)
                    self.send_response(200)
                    write_form(self, operation, result)
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
        fill_duration_bucket(time.time() - start)


if __name__ == "__main__":
    starttime = time.time()
    webServer = HTTPServer((hostName, serverPort), CalcServer)
    print("CalcServer started http://%s:%s" % (hostName, serverPort))
    parser = yacc.yacc()

    if os.environ.get('CALC_VERSION'):
        version = os.environ.get('CALC_VERSION')
    if  os.environ.get('CALC_TESTMODE'):
        testmode = os.environ.get('CALC_TESTMODE')

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("CalcServer stopped.")

