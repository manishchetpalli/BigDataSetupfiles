######FOR LINUX#######
#!/bin/bash
# Generates several self-signed keys <name>.cer, <name>.jks, and <name>.p12.
# Truststore is set with name truststore.jks and set password of password12345
# Usage: createKey.sh <user> <password>
#        createKey.sh somebody password123
# -ext "SAN=DNS:"

export NAME=$1
export IP1=$2
export PASSWORD=7ecETGlHjzs
export STORE_PASSWORD=7ecETGlHjzs

echo "Creating key for $NAME using password $PASSWORD"

keytool -genkey -alias $NAME -keyalg RSA -keysize 4096 -dname "CN=$NAME,OU=ABC,O=ABC,L=BOM,ST=MAH,C=IN" -ext "SAN=DNS:$NAME,IP:$IP1" -keypass $PASSWORD -keystore $NAME.jks -storepass $PASSWORD -validity 7200

keytool -export -keystore $NAME.jks -storepass $PASSWORD -alias $NAME -file $NAME.cer

keytool -import -trustcacerts -file $NAME.cer -alias $NAME -keystore truststore.jks -storepass $STORE_PASSWORD -noprompt

echo "Done creating key for $NAME"

keytool -list -keystore truststore.jks -storepass $STORE_PASSWORD -noprompt



######FOR WINDOWS#######
rem generates several self signed keys <name>.cer, <name>.jks, and <name>.p12 .
rem Truststore is set with name truststore.jks and set password of password12345


rem usage: createKey.bat <user> <password>
rem        createKey.bat somebody password123


rem -ext "SAN=DNS:hostname1.abc.com,DNS:hostname2.abc.com"

set NAME=%1%
set PASSWORD=7ecETGlHjzs
set STORE_PASSWORD=7ecETGlHjzs

echo 'Creating key for ' %NAME% ' using password ' %PASSWORD%


keytool -genkey -alias %NAME% -keyalg RSA -keysize 4096 -dname "CN=$NAME,OU=ABC,O=ABC,L=BOM,ST=MAH,C=IN" -ext "SAN=DNS:%NAME%" -keypass %PASSWORD% -keystore  %NAME%.jks -storepass %PASSWORD% -validity 3650

keytool -importkeystore -srckeystore  %NAME%.jks -destkeystore %NAME%.p12 -srcstoretype JKS -deststoretype PKCS12 -srcstorepass %PASSWORD% -deststorepass %PASSWORD% -srcalias %NAME% -destalias %NAME% -srckeypass %PASSWORD% -destkeypass %PASSWORD% -noprompt

keytool -export -keystore  %NAME%.jks -storepass %PASSWORD% -alias %NAME% -file %NAME%.cer

rem #keytool -import -trustcacerts -file %NAME%.cer -alias %NAME% -keystore truststore.jks -storepass %STORE_PASSWORD% -noprompt
keytool -import -trustcacerts -file %NAME%.cer -alias %NAME% -keystore truststore.jks -storepass %STORE_PASSWORD% -noprompt

echo 'Done creating key for ' %NAME%

keytool -list -keystore truststore.jks -storepass 7ecETGlHjzs -noprompt






######JKS TO PEM#######
/opt/jdk1.8.0_151/bin/keytool -exportcert -alias hostname03.abc.com -keystore truststore.jks -storepass 7ecETGlHjzs -file hostname03.abc.com.crt
/opt/jdk1.8.0_151/bin/keytool -exportcert -alias hostname02.abc.com -keystore truststore.jks -storepass 7ecETGlHjzs -file hostname02.abc.com.crt
/opt/jdk1.8.0_151/bin/keytool -exportcert -alias hostname01.abc.com -keystore truststore.jks -storepass 7ecETGlHjzs -file hostname01.abc.com.crt

openssl x509 -inform der -in hostname03.abc.com.crt -out hostname03.abc.com.pem
openssl x509 -inform der -in hostname02.abc.com.crt -out hostname02.abc.com.pem
openssl x509 -inform der -in hostname01.abc.com.crt -out hostname01.abc.com.pem

cat *.pem > truststore_combined.pem