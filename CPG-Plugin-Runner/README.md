# CPG Plugin Runner

## Introduction

CPG Plugin Runner is a lightweight executable JAR that dynamically loads your access-control plugin JARs from a specified path (either absolute or relative). It evaluates plugins based on the configuration mapping and user-provided input (such as username, resources and actions).

We provide:
- The runner (CPG-Plugin-Runner-1.0.0.jar)
- The plugin-template project for your own plugin development.

Inputs required:
- Your plugin JAR(s) (in PF4J format), and
- A policy mapping file defining which plugins should run for which resources.

## Architecture

### CPG-Plugin-Runner

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           CPG Plugin Runner                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐    │
│  │  Plugin Loader  │      │ Resource Mapper │      │  Input Handler  │    │
│  │  (PF4J-based)   │◄────►│ (YAML Config)   │◄────►│  (Interactive)  │    │
│  └────────┬────────┘      └─────────────────┘      └────────┬────────┘    │
│           │                                                 │             │
│           ▼                                                 ▼             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      Plugin Execution Engine                        │  │
│  └────────────────────────────────┬──────────────────────────────────┬─┘  │
│                                   │                                  │    │
└───────────────────────────────────┼──────────────────────────────────┼────┘
                                    │                                  │
                                    ▼                                  ▼
                ┌─────────────────────────────┐      ┌─────────────────────────────┐
                │      Plugin Instance 1      │      │      Plugin Instance 2      │
                │  (e.g., java-access-plugin) │      │  (e.g.,ranger-access-plugin)│
                └─────────────────────────────┘      └─────────────────────────────┘
                              │                                    │
                              ▼                                    ▼
                ┌─────────────────────────────┐      ┌─────────────────────────────┐
                │    Access Control Logic     │      │    Access Control Logic     │
                │    - Permission checking    │      │    - Permission checking    │
                │    - Resource evaluation    │      │    - Resource evaluation    │
                │    - Row/column transforms  │      │    - Row/column transforms  │
                └─────────────────────────────┘      └─────────────────────────────┘
```

### Access Plugin
```
┌─────────────────────────────────────────────────────────────────┐
│                     CPG Plugin Runner System                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Plugin API (CPG-Plugin-Runner.jar)         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Java Access Plugin                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐           ┌───────────────────────────┐    │
│  │   PluginEntry   │           │         Plugin            │    │
│  │  (Entry Point)  │──────────▶│(AccessEvaluationPlugin)   │    │
│  └─────────────────┘           └───────────────┬───────────┘    │
│                                                │                │
│                                                ▼                │
│                                ┌───────────────────────────┐    │
│                                │  Resource Evaluation      │    │
│                                │  - Permissions checking   │    │
│                                │  - Action authorization   │    │
│                                └───────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

The deliverables in the repo will look like this:

```
CPG-Plugin-Runner/
├─ CPG-Plugin-Runner-1.0.0.jar      # The executable runner
├─ plugins/                         # Place your plugin JARs here
│  └─ <your-plugin>.jar
├─ config/
   └─ plugin-resource-mapping.yaml  # Maps resource names to plugin IDs
├─ plugin-templates
   └─ java-access-plugin            # sample plugin project
      ├─ src
      └─ resources
         └─ plugin.properties
```

You may rename or move folders as needed. Use the Run options (below) to point CPG to different paths.

## Configuration File - plugin-resource-mapping.yaml

### Example

```yaml
plugin-mapping:
  java-access-plugin:
    - iceberg
  ranger-access-plugin:
    - iceberg
    - hive_data
  python-access-plugin:
    - hive_data
```

### Explanation

- Keys: Plugin IDs, defined in each plugin's plugin.properties file (e.g., `plugin.id=java-access-plugin`). The ID must match exactly.
- Values: Resource names that the plugin applies to.
- Special value: Use `ALL` to apply a plugin to all resources.

## Runner Behavior

When executed, the runner:

1. Discovers your plugin(s)
2. Starts them
3. Prompts for:
   - Username
   - Resource name (e.g., hive_data)
   - Resource type (e.g., table, catalog, etc.)
   - Actions (comma-separated, e.g., select,insert)
4. Executes the configured plugins and prints results, including optional row/column transforms if defined by your plugin.

## Running the Runner

### Default Run

Uses the default locations:
- plugins/ → ./plugins
- config/  → ./config/plugin-resource-mapping.yaml

Command:
```bash
java -jar CPG-Plugin-Runner-1.0.0.jar
```

### Custom Paths

You can specify explicit plugin and config paths:

```bash
java -jar CPG-Plugin-Runner-1.0.0.jar <absolute/path/to/plugins> <absolute/path/to/config/plugin-resource-mapping.yaml>
```

Or specify just the config file (must have .yaml or .yml extension):

```bash
java -jar CPG-Plugin-Runner-1.0.0.jar <absolute/path/to/config/plugin-resource-mapping.yaml>
```

### System Properties

You can also use system properties to override paths:

```bash
java -Dcpg.plugin.dir=/path/to/plugins -Dcpg.config.file=/path/to/config.yaml -jar CPG-Plugin-Runner-1.0.0.jar
```

Other system properties:
- `cpg.verbose`: Enable verbose logging (true/false)
- `cpg.boot`: Enable boot console (true/false)
- `cpg.boot.banner`: Show banner (true/false)
- `cpg.boot.spinner`: Show spinner (true/false)

## Sample Interactive Session

```
Enter username : admin
Enter resource_name (e.g., hive_data) or 'quit': hive_data
Enter resource_type (e.g., table): table
Enter actions (comma-separated, e.g., select,insert): select

[Runner] Params: user=admin, resource=hive_data, type=table, actions=[select]
[Runner] Plugins to run: [java-access-plugin]
======Result======
{
  "status" : "SUCCESS",
  "error" : null,
  "plugin_id" : "java-access-plugin",
  "resources" : [ {
    "actions" : [ "select" ],
    "resource_name" : "hive_data",
    "resource_type" : "table",
    "actions_result" : [ {
      "select" : "true"
    } ],
    "transform_columns" : null,
    "transform_rows" : null
  } ]
}
=================
```

Type `quit` or `exit` at any prompt to stop, or press Ctrl+C.

## Developing and Supplying Your Plugin

1. Place your plugin JAR(s) in the plugins/ directory.
2. Add your plugin ID under the desired resource in config/plugin-resource-mapping.yaml.
3. Re-run:
   ```bash
   java -jar CPG-Plugin-Runner-1.0.0.jar
   ```
4. Your plugin will automatically be discovered and executed.

## Building a Plugin (from Template)

A plugin template project is included. It compiles against the API types already embedded in CPG-Plugin-Runner-1.0.0.jar - no extra dependencies required.

### Steps

1. Download the template.
2. Modify as needed.
3. Build:
   ```bash
   cd java-access-plugin
   mvn -DskipTests clean package
   ```
4. Your JAR will be generated at:
   ```
   target/<your-plugin>.jar
   ```
5. Deploy:
   - Copy the JAR into the runner's plugins/ folder.
   - Update plugin-resource-mapping.yaml to reference your plugin ID.
   - Run CPG as described above.

Optional: To return row/column transforms, set them via:
```java
result.setTransformColumns(...); 
result.setTransformRows(...);
```

## Implementing a Plugin

### plugin.properties

Every plugin must include a `plugin.properties` file in the resources directory:

```properties
plugin.id=java-access-plugin
plugin.version=2.0.0
plugin.class=com.plugin.PluginEntry
```

Required fields:
- `plugin.id`: Unique identifier for your plugin
- `plugin.version`: Version of your plugin
- `plugin.class`: Fully qualified name of your plugin class

### Plugin Class Structure

1. Create a plugin class that extends `org.pf4j.Plugin`:

```java
package com.yourcompany;

import org.pf4j.Plugin;
import org.pf4j.PluginWrapper;

public class YourPlugin extends Plugin {
    public YourPlugin(PluginWrapper wrapper) {
        super(wrapper);
    }

    @Override
    public void start() {
        // Plugin initialization code
    }

    @Override
    public void stop() {
        // Plugin cleanup code
    }
}
```

2. Create an extension that implements `AccessEvaluationPlugin`:

```java
package com.yourcompany;

import com.cpg.plugin.AccessEvaluationPlugin;
import com.cpg.plugin.dto.PluginEvaluationRequest;
import com.cpg.plugin.dto.PluginEvaluationResponse;
import org.pf4j.Extension;

import java.util.List;

@Extension
public class YourExtension implements AccessEvaluationPlugin {
    
    @Override
    public void init() {
        // Initialization logic
    }
    
    @Override
    public List<PluginEvaluationResponse> evaluate(List<PluginEvaluationRequest> accessRequests) {
        // Your evaluation logic here
        // Process the accessRequests and return responses
    }
}
```

### Maven POM Example

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.yourcompany</groupId>
    <artifactId>your-plugin</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.release>17</maven.compiler.release>
        <pf4j.version>3.10.0</pf4j.version>
    </properties>
    
    <dependencies>
        <!-- PF4J -->
        <dependency>
            <groupId>org.pf4j</groupId>
            <artifactId>pf4j</artifactId>
            <version>${pf4j.version}</version>
            <scope>provided</scope>
        </dependency>
        
        <!-- CPG Plugin API - This should be provided by your organization -->
        <dependency>
            <groupId>com.cpg.plugin</groupId>
            <artifactId>cpg-plugin-api</artifactId>
            <version>1.0.0</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.13.0</version>
                <configuration>
                    <release>${maven.compiler.release}</release>
                </configuration>
            </plugin>
            
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.4.1</version>
                <configuration>
                    <archive>
                        <manifestEntries>
                            <Plugin-Id>${project.artifactId}</Plugin-Id>
                            <Plugin-Version>${project.version}</Plugin-Version>
                            <Plugin-Class>com.yourcompany.YourPlugin</Plugin-Class>
                        </manifestEntries>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

## Troubleshooting

### Error: "No AccessPlugin extensions found"

Check that:
- The plugins/ directory exists and is not empty.
- The JAR includes plugin.properties at its root.
- Your plugin class is annotated with @Extension and implements AccessEvaluationPlugin.
- The plugin.id in plugin.properties matches the ID in plugin-resource-mapping.yaml.

### Plugin Not Running for Resource

- Verify that your resource name in plugin-resource-mapping.yaml maps correctly to the plugin ID.
- Ensure IDs match exactly (case-sensitive).

### Custom Paths Not Picked Up

- Use absolute paths.
- Or pass them via system properties.

## Compatibility and Platform Notes

- Tested on: macOS
- Windows: Testing pending (should function, but verification recommended).
- JDK Compatibility: Tested on JDK 11-17 (recommended: JDK 17+)

### Known Limitations:

- Currently supports PF4J-based plugins only.
- No GUI interface; runs via command-line.
- Path resolution may vary between OS environments.

## API Reference

### AccessEvaluationPlugin Interface

```java
public interface AccessEvaluationPlugin extends ExtensionPoint {
    default void init() {}
    default void transform() {}
    default List<PluginEvaluationResponse> evaluate(List<PluginEvaluationRequest> accessRequests) {
        throw new UnsupportedOperationException("This plugin does not support structured evaluate()");
    }
}
```

### PluginEvaluationRequest Class

```java
public class PluginEvaluationRequest {
    private String username;
    private List<Resource> resources;
    // Getters and setters
}
```

### PluginEvaluationResponse Class

```java
public class PluginEvaluationResponse {
    private String pluginId;
    private EvaluationStatus status; // SUCCESS, DENIED, ERROR, UNAVAILABLE
    private String error;
    private List<ResourceEvaluationResult> resources;
    // Getters and setters
}
```

### Resource Class

```java
public class Resource {
    private String resourceName;
    private String resourceType;
    private List<String> actions;
    // Getters and setters
}
```

### ResourceEvaluationResult Class

```java
public class ResourceEvaluationResult {
    private String resourceName;
    private String resourceType;
    private List<String> actions;
    private List<Map<String, String>> actionsResult;
    private Object transformColumns;
    private Object transformRows;
    // Getters and setters
}