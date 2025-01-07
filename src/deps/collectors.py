def dbapiDep(config):
    deps = ['SQLAlchemy']
    dbUrl = config.dbUrl
    mapping = [
        ['mysql+mysqlconnector','mysql-connector-python'],
        ['mysql+mysqldb','mysqlclient'],
        ['mysql+pymysql','PyMySQL'],
        ['mssql+pyodbc','pyodbc'],
        ['oracle://','cx_oracle'],
        ['oracle+oracledb','oracledb']
    ]
    for m in mapping:
        if dbUrl.startswith(m[0]):
            deps.append(m[1])
            break
    return deps
def wordpressDep(config):
    return dbapiDep({'dbUrl':config['connector']}) if 'connector' in config else dbapiDep({'dbUrl':'mysql+mysqlconnector'})
COLLECTORS_DEPS = {
    "csv":None,
    "dbapi":dbapiDep,
    "wordpress":wordpressDep,
    "tester":""
}