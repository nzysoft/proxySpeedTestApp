import sqlite3

class MyDb:
    
    def __init__(self, dbName='database.db'):

        self.conn=sqlite3.connect(dbName)
        c = self.conn.cursor()

    def create(self):
        c = self.conn.cursor()
        with self.conn:
            try:
                c.execute("""create table proxys (
                    time datetime,
                    protocol text,
                    ip text,
                    size real,
                    getfiletime text,
                    speed integer
                    )""")
            except sqlite3.OperationalError as e:
                print(e)

            try:
                c.execute("create table proxysInx (proxysInx datetime)")
            except sqlite3.OperationalError as e:
                print(e)
            
            try:
                c.execute('''create table configs (
                    themeMode text,
                    miInx integer,
                    proxysInx datetime,
                    timeoutD integer,
                    fileSize integer
                    )''')
                c.execute("INSERT INTO configs (themeMode, miInx, timeoutD, fileSize) VALUES ('Dark',0, 5, 1062124)")
            except sqlite3.OperationalError as e:
                print(e)
            
            try:
                self.createMirror()
                c.execute("INSERT INTO mirrors VALUES ('http://bd.archive.ubuntu.com/ubuntu/indices/override.oneiric.universe')")
                c.execute("INSERT INTO mirrors VALUES ('http://provo.speed.googlefiber.net:3004/download?size=1048576')")
            except sqlite3.OperationalError as e:
                print(e)
    
    def createMirror(self):
        c = self.conn.cursor()
        with self.conn:
            c.execute("create table mirrors (mirror text)")
    
    def getAllConfigs(self):
        c = self.conn.cursor()
        with self.conn:
            c.execute("SELECT * FROM 'configs'")
            configs = c.fetchall()
        return configs
    
    def getAllMirrors(self):
        c = self.conn.cursor()
        with self.conn:
            c.execute("SELECT * FROM 'mirrors'")
            mirrors = c.fetchall()
        return mirrors

    def getProxysInx(self):
        c = self.conn.cursor()
        with self.conn:
            c.execute("SELECT proxysInx FROM 'proxysInx'")
            proxysInx = c.fetchall()
        return proxysInx
    
    def getConfig(self, name):
        c = self.conn.cursor()
        with self.conn:
            c.execute(f"SELECT {name} FROM 'configs'")
            config = c.fetchone()
        return config
    
    def getAllCurrentProxys(self, time):
        c = self.conn.cursor()
        with self.conn:
            c.execute("SELECT ip, size, getfiletime, speed, protocol, time FROM 'proxys' WHERE time=?", [time])
            scan_list = c.fetchall()
        return scan_list

    def updateThemeMode(self, name):
        c = self.conn.cursor()
        with self.conn:
            c.execute("UPDATE 'configs' SET themeMode=?", [name])

    def updateScanList(self, l):
        c = self.conn.cursor()
        with self.conn:
            try:
                for p in l:
                    c.execute("UPDATE proxys SET size=?, getfiletime=?, speed=? WHERE ip=?",
                                                (p['SIZE'], p['TIME'], p['SPEED'], p['IP']))
            except sqlite3.OperationalError as e:
                print(e)

    def updateConfig(self, key, value):
        c = self.conn.cursor()
        with self.conn:
            c.execute(f"UPDATE 'configs' SET {key}=?", [value])

    def updateProxysInx(self, new, old):
        c = self.conn.cursor()
        with self.conn:
            c.execute("UPDATE 'proxysInx' SET proxysInx=? WHERE proxysInx=?", (new, old))

    def updateProxys(self, new, old):
        c = self.conn.cursor()
        with self.conn:
            c.execute("UPDATE 'proxys' SET time=?, size=NULL, getfiletime=NULL, speed=NULL WHERE time=?", (new, old))

    def createProxysList(self, proxys, protocol, IndexTime):
        c = self.conn.cursor()
        with self.conn:
            for l in proxys:
                if not l:continue
                try:
                    c.execute('INSERT INTO proxys (time, ip, protocol) VALUES (?, ?, ?)', (IndexTime, l, protocol))
                except sqlite3.OperationalError as e:
                    print(e)

            self.updateConfig('proxysInx', IndexTime)
            c.execute("INSERT INTO proxysInx VALUES (?)", [IndexTime])
    
    def drop(self, name):
        c = self.conn.cursor()
        with self.conn:
            c.execute(f"DROP TABLE '{name}'")
    
    def inputeMirror(self, l):
        self.drop('mirrors')
        self.createMirror()
        
        c = self.conn.cursor()
        with self.conn:
            for line in l:  
                if not line == '':
                    c.execute("INSERT INTO mirrors VALUES (?)", [line.strip()])

        self.updateConfig('miInx', 0)
