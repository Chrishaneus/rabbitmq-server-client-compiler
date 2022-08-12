import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import spoon.Launcher;
import spoon.reflect.code.CtBlock;
import spoon.reflect.code.CtCodeSnippetStatement;
import spoon.reflect.code.CtFor;
import spoon.reflect.code.CtForEach;
import spoon.reflect.code.CtLocalVariable;
import spoon.reflect.code.CtStatement;
import spoon.reflect.code.CtWhile;
import spoon.reflect.declaration.CtClass;
import spoon.reflect.declaration.CtElement;
import spoon.reflect.declaration.CtField;
import spoon.reflect.declaration.CtImport;
import spoon.reflect.declaration.CtMethod;
import spoon.reflect.declaration.CtRecordComponent;
import spoon.reflect.declaration.CtType;
import spoon.reflect.declaration.ModifierKind;
import spoon.reflect.factory.Factory;
import spoon.reflect.factory.FactoryImpl;
import spoon.reflect.reference.CtTypeReference;
import spoon.reflect.visitor.CtAbstractVisitor;
import spoon.reflect.visitor.CtScanner;
import spoon.reflect.visitor.CtVisitor;
import spoon.reflect.visitor.ImportScanner;
import spoon.reflect.visitor.ImportScannerImpl;
import spoon.support.DefaultCoreFactory;
import spoon.support.StandardEnvironment;

public class App {
    static class InjectVisitor extends CtScanner {
        Factory factory;
        String className;
        final String loop_counter = "AZEUS_LOOP_COUNTER";
        final String call_counter = "AZEUS_CALL_COUNTER";

        public InjectVisitor(String className){
            this.factory = new FactoryImpl(new DefaultCoreFactory(), new StandardEnvironment());
            this.className = className;
        }

		@Override
		public <T> void visitCtMethod(CtMethod<T> m) {
			super.visitCtMethod(m);

            if (m.getSimpleName().equals("main")){
                List<CtStatement> bodyStatements = m.getBody().getStatements();
                int size = bodyStatements.size();
                bodyStatements.add(size, factory.Code().createCodeSnippetStatement("System.out.println(\""+loop_counter+" = \" + Integer.toString("+loop_counter+"))"));
                bodyStatements.add(size, factory.Code().createCodeSnippetStatement("System.out.println(\""+call_counter+" = \" + Integer.toString("+call_counter+"))"));
            }
            else{
                List<CtStatement> bodyStatements = m.getBody().getStatements();
                bodyStatements.add(0, factory.Code().createCodeSnippetStatement(call_counter + " += 1"));
            }
		}

        @Override
        public <T> void visitCtClass(CtClass<T> ctClass) {
            super.visitCtClass(ctClass);

            if (ctClass.getSimpleName().equals(this.className)){
                ctClass.addField(0, factory.createCtField(loop_counter, factory.Type().integerPrimitiveType(), "0", ModifierKind.STATIC));
                ctClass.addField(0, factory.createCtField(call_counter, factory.Type().integerPrimitiveType(), "0", ModifierKind.STATIC));
            }
        }

        @Override
        public void visitCtFor(CtFor forLoop) {
            super.visitCtFor(forLoop);
            forLoop.getBody().insertBefore(factory.Code().createCodeSnippetStatement(loop_counter + " += 1"));
        }

        @Override
        public void visitCtForEach(CtForEach foreach) {
            super.visitCtForEach(foreach);
            foreach.getBody().insertBefore(factory.Code().createCodeSnippetStatement(loop_counter + " += 1"));
        }

        @Override
        public void visitCtWhile(CtWhile whileLoop) {
            super.visitCtWhile(whileLoop);
            whileLoop.getBody().insertBefore(factory.Code().createCodeSnippetStatement(loop_counter + " += 1"));
        }
	}
    
    public static void main(String[] args) throws Exception {
        String inTextContent = Files.readString(Path.of("./in.txt"));
        CtClass ast;
        switch (args[0]){
            case "getclassname":
                try {
                    ast = Launcher.parseClass(inTextContent);
                    Files.writeString(Path.of("./out.txt"), ast.getSimpleName());
                    Files.writeString(Path.of("./error.txt"), "");
                } catch (Exception e) {
                    Files.writeString(Path.of("./out.txt"), "");
                    Files.writeString(Path.of("./error.txt"), e.toString());
                }
                break;
            case "inject":
                try {
                    ast = Launcher.parseClass(inTextContent);
                    InjectVisitor injectVisitor = new InjectVisitor(ast.getSimpleName());
                    ast.accept(injectVisitor);

                    Files.writeString(Path.of("./out.txt"), getImports(ast) + ast.toString());
                    Files.writeString(Path.of("./error.txt"), "");
                } catch (Exception e) {
                    Files.writeString(Path.of("./out.txt"), "");
                    Files.writeString(Path.of("./error.txt"), e.toString());
                }
                break;
            default:
                System.out.println("Unknown command " + args[0]);
                break;
        }
    }

    public static String getImports(CtClass ast){
        ImportScanner importScanner = new ImportScannerImpl();
        importScanner.computeImports(ast);
        Set<CtImport> importSet = importScanner.getAllImports();
        String imports = "";
        for (CtImport imp : importSet)
            imports += imp.toString() + "\n";
        return imports;
    }
}