FROM maven:3.9.6-eclipse-temurin-8 AS build
WORKDIR /workspace

# Pre-copy POMs to leverage Docker layer caching for dependencies
COPY pom.xml /workspace/pom.xml
COPY server/pom.xml /workspace/server/pom.xml
COPY webapp/pom.xml /workspace/webapp/pom.xml
RUN mvn -q -B -e -DskipTests dependency:go-offline

# Build full project
COPY . /workspace
RUN mvn -q -B -e -DskipTests package

# Runtime image
FROM tomcat:9.0-jdk8-temurin
RUN rm -rf /usr/local/tomcat/webapps/* && mkdir -p /usr/local/tomcat/webapps
COPY --from=build /workspace/webapp/target/webapp.war /usr/local/tomcat/webapps/ROOT.war

EXPOSE 8080
CMD ["catalina.sh", "run"]

