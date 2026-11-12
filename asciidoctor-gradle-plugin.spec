Name:		asciidoctor-gradle-plugin
Version:	5.1.0
Release:	1
Summary:	Asciidoctor Gradle plugins
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/asciidoctor/asciidoctor-gradle-plugin
# Tag release_5_1_0. This builds asciidoctoreditorconfig and
# asciidoctor5-core-plugin with Groovy's FileSystemCompiler.
# The Gradle tool is not invoked. asciidoctor5-jvm-core-plugin is in
# the same tag and is not built here: it compiles against the JRuby
# resolver plugin.
Source0:	asciidoctor-gradle-plugin-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	gradle
BuildRequires:	apache-groovy
BuildRequires:	antlr4
BuildRequires:	objectweb-asm
BuildRequires:	picocli
BuildRequires:	jansi
BuildRequires:	apache-commons-io
BuildRequires:	ant-lib
BuildRequires:	slf4j2
BuildRequires:	mvn(org.ysb33r.gradle:grolifant5-core) = 5.12.7
BuildRequires:	mvn(org.ysb33r.gradle:grolifant5-rawhide) = 5.12.7
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
Requires:	gradle
Requires:	apache-groovy

%description
org.asciidoctor:asciidoctoreditorconfig and
org.asciidoctor:asciidoctor5-core-plugin %{version}. DocType.from
parses a document type name and SafeMode.from maps a level to a mode.
The main sources are compiled with FileSystemCompiler at bytecode 11.
The Gradle tool is not invoked.

%prep
%autosetup -n asciidoctor-gradle-plugin-release_5_1_0 -p1
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
find . -type d -name '*.jar' -print >> binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
find model5/asciidoctoreditorconfig/src/main -type f \( -name '*.groovy' -o -name '*.java' \) | sort > editorconfig.list
find model5/core/src/main -type f \( -name '*.groovy' -o -name '*.java' \) | sort > core.list
test "$(wc -l < editorconfig.list)" -eq 2
test "$(grep -c '\.groovy$' editorconfig.list)" -eq 2
test "$(wc -l < core.list)" -eq 120
test "$(grep -c '\.groovy$' core.list)" -eq 65
test "$(grep -c '\.java$' core.list)" -eq 55

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
tool_cp=%{_javadir}/apache-groovy.jar
for extra in \
	%{_javadir}/antlr4-runtime.jar \
	%{_javadir}/asm.jar \
	%{_javadir}/asm-commons.jar \
	%{_javadir}/asm-tree.jar \
	%{_javadir}/asm-util.jar \
	%{_javadir}/asm-analysis.jar \
	%{_javadir}/picocli.jar \
	/usr/lib/java/jansi/jansi.jar
do
	test -s "$extra"
	tool_cp=$tool_cp:$extra
done
gradle_cp=
for j in %{_datadir}/gradle/lib/*.jar %{_datadir}/gradle/lib/plugins/*.jar; do
	test -s "$j"
	base=$(basename "$j")
	case "$base" in
	antlr4-runtime-*|asm-9*.jar|asm-commons-*|asm-tree-*|asm-util-*|asm-analysis-*)
		continue
		;;
	esac
	if [ -z "$gradle_cp" ]; then
		gradle_cp=$j
	else
		gradle_cp=$gradle_cp:$j
	fi
done
test -n "$gradle_cp"
src_cp=$gradle_cp:%{_javadir}/grolifant5-core.jar:%{_javadir}/grolifant5-rawhide.jar:%{_javadir}/commons-io.jar:%{_javadir}/ant.jar:%{_javadir}/slf4j-api.jar

mkdir -p editorconfig-classes
java -Dgroovy.target.bytecode=11 -cp "$tool_cp:$src_cp" org.codehaus.groovy.tools.FileSystemCompiler \
	--classpath "$src_cp" -j '-J-release=11' -d editorconfig-classes @editorconfig.list
test "$(find editorconfig-classes -name '*.class' | wc -l)" -eq 9
javap -v -classpath editorconfig-classes org.asciidoctor.gradle.model5.editorconfig.AsciidoctorEditorConfigPlugin | grep -F -q 'major version: 55'
mkdir -p editorconfig-classes/META-INF/gradle-plugins
printf '%s\n' 'implementation-class=org.asciidoctor.gradle.model5.editorconfig.AsciidoctorEditorConfigPlugin' \
	> editorconfig-classes/META-INF/gradle-plugins/org.asciidoctor.editorconfig.properties
printf '%s\n' 'Manifest-Version: 1.0' 'Automatic-Module-Name: org.asciidoctor.asciidoctoreditorconfig' > editorconfig.mf
jar cfm asciidoctoreditorconfig.jar editorconfig.mf -C editorconfig-classes .
jar i asciidoctoreditorconfig.jar
jar tf asciidoctoreditorconfig.jar | grep -F -q 'org/asciidoctor/gradle/model5/editorconfig/AsciidoctorEditorConfigGenerator.class'
jar tf asciidoctoreditorconfig.jar | grep -F -q 'META-INF/gradle-plugins/org.asciidoctor.editorconfig.properties'

src_cp=$src_cp:editorconfig-classes
mkdir -p core-classes
java -Dgroovy.target.bytecode=11 -cp "$tool_cp:$src_cp" org.codehaus.groovy.tools.FileSystemCompiler \
	--classpath "$src_cp" -j '-J-release=11' -d core-classes @core.list
test "$(find core-classes -name '*.class' | wc -l)" -eq 269
javap -v -classpath core-classes org.asciidoctor.gradle.model5.core.SafeMode | grep -F -q 'major version: 55'
javap -v -classpath core-classes org.asciidoctor.gradle.model5.core.DocType | grep -F -q 'major version: 55'
javap -v -classpath core-classes org.asciidoctor.gradle.model5.core.plugins.AsciidoctorCorePlugin | grep -F -q 'major version: 55'
mkdir -p core-classes/META-INF/gradle-plugins
printf '%s\n' 'implementation-class=org.asciidoctor.gradle.model5.core.plugins.AsciidoctorCoreBasePlugin' \
	> core-classes/META-INF/gradle-plugins/org.asciidoctor.core.base.properties
printf '%s\n' 'implementation-class=org.asciidoctor.gradle.model5.core.plugins.AsciidoctorCorePlugin' \
	> core-classes/META-INF/gradle-plugins/org.asciidoctor.core.properties
printf '%s\n' 'implementation-class=org.asciidoctor.gradle.model5.core.plugins.AsciidoctorCoreThemesPlugin' \
	> core-classes/META-INF/gradle-plugins/org.asciidoctor.themes.properties
printf '%s\n' 'Manifest-Version: 1.0' 'Automatic-Module-Name: org.asciidoctor.asciidoctor5.core.plugin' > core.mf
jar cfm asciidoctor5-core-plugin.jar core.mf -C core-classes .
jar i asciidoctor5-core-plugin.jar
jar tf asciidoctor5-core-plugin.jar | grep -F -q 'org/asciidoctor/gradle/model5/core/SafeMode.class'
jar tf asciidoctor5-core-plugin.jar | grep -F -q 'META-INF/gradle-plugins/org.asciidoctor.core.properties'

for jar in asciidoctoreditorconfig.jar asciidoctor5-core-plugin.jar; do
	desc=$(jar --describe-module --file "$jar")
	printf '%s\n' "$desc"
	if printf '%s\n' "$desc" | grep -F -q 'Unable'; then
		exit 1
	fi
done
printf '%s\n' "$desc" | grep -F -q 'org.asciidoctor.asciidoctor5.core.plugin'

cat > asciidoctoreditorconfig.pom << 'END'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.asciidoctor</groupId>
  <artifactId>asciidoctoreditorconfig</artifactId>
  <version>5.1.0</version>
  <name>asciidoctoreditorconfig</name>
  <description>Generates .asciidoctorconfig files for supported IDEs.</description>
  <url>https://github.com/asciidoctor/asciidoctor-gradle-plugin</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.ysb33r.gradle</groupId>
      <artifactId>grolifant5-core</artifactId>
      <version>5.12.7</version>
    </dependency>
    <dependency>
      <groupId>org.ysb33r.gradle</groupId>
      <artifactId>grolifant5-herd</artifactId>
      <version>5.12.7</version>
      <scope>runtime</scope>
    </dependency>
  </dependencies>
</project>
END

cat > asciidoctor5-core-plugin.pom << 'END'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.asciidoctor</groupId>
  <artifactId>asciidoctor5-core-plugin</artifactId>
  <version>5.1.0</version>
  <name>asciidoctor5-core-plugin</name>
  <description>Core plugins for Asciidoctor on Gradle.</description>
  <url>https://github.com/asciidoctor/asciidoctor-gradle-plugin</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.ysb33r.gradle</groupId>
      <artifactId>grolifant5-core</artifactId>
      <version>5.12.7</version>
    </dependency>
    <dependency>
      <groupId>org.ysb33r.gradle</groupId>
      <artifactId>grolifant5-herd</artifactId>
      <version>5.12.7</version>
      <scope>runtime</scope>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact asciidoctoreditorconfig.pom:asciidoctoreditorconfig.jar \
	--file-name asciidoctoreditorconfig \
	--filelist .mfiles-editor
sysjar install --buildroot %{buildroot} \
	--artifact asciidoctor5-core-plugin.pom:asciidoctor5-core-plugin.jar \
	--file-name asciidoctor5-core-plugin \
	--filelist .mfiles-core
: > .mfiles
for list in .mfiles-editor .mfiles-core; do
	while IFS= read -r line; do
		grep -qxF "$line" .mfiles || printf '%%s\n' "$line" >> .mfiles
	done < "$list"
done
idx="%{buildroot}/usr/share/sysjar/index/org.asciidoctor/asciidoctor5-core-plugin.sysjar"
test -s "$idx"
grep -F -q '"version": "5.1.0"' "$idx"
grep -F -q '"artifactId": "asciidoctor5-core-plugin"' "$idx"
test -s %{buildroot}%{_javadir}/asciidoctoreditorconfig.jar
test -s %{buildroot}%{_javadir}/asciidoctor5-core-plugin.jar

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
CORE=%{buildroot}%{_javadir}/asciidoctor5-core-plugin.jar
EDITOR=%{buildroot}%{_javadir}/asciidoctoreditorconfig.jar
test -s "$CORE"
test -s "$EDITOR"
gradle_cp=
for j in %{_datadir}/gradle/lib/*.jar %{_datadir}/gradle/lib/plugins/*.jar; do
	test -s "$j"
	if [ -z "$gradle_cp" ]; then
		gradle_cp=$j
	else
		gradle_cp=$gradle_cp:$j
	fi
done
CP="$CORE:$EDITOR:%{_javadir}/apache-groovy.jar:%{_javadir}/grolifant5-core.jar:$gradle_cp"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import org.asciidoctor.gradle.model5.core.DocType;
import org.asciidoctor.gradle.model5.core.SafeMode;

public class Smoke {
    public static void main(String[] args) {
        DocType book = DocType.from("book");
        if (!"book".equals(book.lc())) {
            throw new AssertionError(book.lc());
        }
        SafeMode mode = SafeMode.from(1);
        if (mode.getLevel() != 1) {
            throw new AssertionError(mode.getLevel());
        }
        System.out.println("asciidoctor_core_ok " + book.lc() + " " + mode.getLevel());
    }
}
EOF
javac --release 11 -Xlint:-options -cp "$CP" -d check check/Smoke.java
"$JAVA_HOME/bin/java" -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -qx 'asciidoctor_core_ok book 1' check/out.txt

%files -f .mfiles
%doc README.adoc
%license LICENSE
