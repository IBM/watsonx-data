/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.facebook.presto.plugin.snowflake;

import com.facebook.airlift.log.Logger;

import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;
import java.util.concurrent.ThreadLocalRandom;

import static java.lang.Thread.sleep;
import static java.util.Objects.requireNonNull;

public class TestingSnowflakeServer
{
    private static final Logger logger = Logger.get(TestingSnowflakeServer.class);
    private static final char[] ALPHABET = new char[36];

    static {
        for (int digit = 0; digit < 10; digit++) {
            ALPHABET[digit] = (char) ('0' + digit);
        }

        for (int letter = 0; letter < 26; letter++) {
            ALPHABET[10 + letter] = (char) ('a' + letter);
        }
    }
    private static final int RANDOM_SUFFIX_LENGTH = 10;
    private static final SecureRandom random = new SecureRandom();
    public static final String TEST_URL = requireNonNull(System.getProperty("snowflake.test.server.url"), "snowflake.test.server.url is not set");
    public static final String TEST_USER = requireNonNull(System.getProperty("snowflake.test.server.user"), "snowflake.test.server.user is not set");
    public static final String TEST_PASSWORD = requireNonNull(System.getProperty("snowflake.test.server.password"), "snowflake.test.server.password is not set");
    public static final String TEST_DATABASE = requireNonNull(System.getProperty("snowflake.test.server.database"), "snowflake.test.server.database is not set");
    public static final String TEST_ROLE = requireNonNull(System.getProperty("snowflake.test.server.role"), "snowflake.test.server.role is not set");
    public static final String TEST_SCHEMA = requireNonNull(System.getProperty("snowflake.test.server.schema"), "snowflake.test.server.schema is not set");

    private TestingSnowflakeServer() {}

    public static void execute(String sql)
    {
        execute(TEST_URL, getProperties(), sql);
    }

    public static void execute(String url, Properties properties, String sql)
    {
        try (Connection connection = getConnection(url, properties);
                Statement statement = connection.createStatement()) {
            statement.execute(sql);
        }
        catch (SQLException | InterruptedException e) {
            logger.error(e, "Failed to execute statement");
            throw new RuntimeException(e);
        }
    }
    public static int executeAndGetCount(String url, Properties properties, String query)
    {
        try (Connection connection = getConnection(url, properties);
                Statement statement = connection.createStatement();
                ResultSet resultSet = statement.executeQuery(query)) {
            if (resultSet.next()) {
                return resultSet.getInt(1);
            }
        }
        catch (SQLException | InterruptedException e) {
            logger.error(e, "Failed to execute statement and get count");
            throw new RuntimeException(e);
        }
        return 0;
    }

    public static Connection getConnection(String url, Properties properties) throws SQLException, InterruptedException
    {
        for (int retries = 0; retries < 5; retries++) {
            try {
                return DriverManager.getConnection(url, properties);
            }
            catch (SQLException e) {
                if (retries < 4) {
                    logger.info(e + " Failed to establish connection after " + (retries + 1) + " retry attempt(s).");
                }
                //sleep between retries
                sleep(ThreadLocalRandom.current().nextLong(1000) * (retries + 1));
                logger.info("Retrying");
            }
        }
        throw new SQLException("Failed to establish connection after all retry attempts");
    }

    public static void dropTable(String url, String tableName)
    {
        String dropTableSQL = "DROP TABLE " + tableName;
        execute(url, getProperties(), dropTableSQL);
    }

    public static void dropTableIfExists(String url, String tableName)
    {
        String dropTableIfExistsSQL = "DROP TABLE IF EXISTS " + tableName;
        execute(url, getProperties(), dropTableIfExistsSQL);
    }
    public static Properties getProperties()
    {
        Properties properties = new Properties();
        properties.setProperty("user", TEST_USER);
        properties.setProperty("password", TEST_PASSWORD);
        properties.setProperty("db", TEST_DATABASE);
        properties.setProperty("schema", TEST_SCHEMA);
        properties.setProperty("role", TEST_ROLE);
        properties.setProperty("schema", TEST_SCHEMA);
        return properties;
    }

    public static String randomNameSuffix()
    {
        char[] chars = new char[RANDOM_SUFFIX_LENGTH];
        for (int i = 0; i < chars.length; i++) {
            chars[i] = ALPHABET[random.nextInt(ALPHABET.length)];
        }
        return new String(chars);
    }
}
