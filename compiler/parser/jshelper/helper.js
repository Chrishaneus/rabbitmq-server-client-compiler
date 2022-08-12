const fs = require('fs');
const esprima = require("esprima")
const traverse = require("ast-traverse");
const escodegen = require("escodegen");

commands = [
  ["injectjs", (dataIn, args) => {
    let dataOut = "";
    let dataError = "";
    
    const loop_counter = "AZEUS_LOOP_COUNTER"
    const call_counter = "AZEUS_CALL_COUNTER"

    node_counter1 = esprima.parseScript(`let ${loop_counter} = 0;`).body[0]
    node_counter2 = esprima.parseScript(`let ${call_counter} = 0;`).body[0]
    node_increment_loop = esprima.parseScript(`${loop_counter}++;`).body[0]
    node_increment_call = esprima.parseScript(`${call_counter}++;`).body[0]
    node_count = esprima.parseScript(`console.log('\\n${loop_counter} = ' + ${loop_counter}.toString() + '\\n${call_counter} = ' + ${call_counter}.toString())`).body[0]

    const ast = esprima.parseScript(dataIn);

    const innerArrowFunction = ast.body[0].expression.arguments[1].body
    innerArrowFunction.body.splice(0,0,node_counter1)
    innerArrowFunction.body.splice(0,0,node_counter2)
    innerArrowFunction.body.splice(innerArrowFunction.body.length,0,node_count)

    traverse(ast, {post: function(node, parent) {
        switch(node.type){
          case "FunctionDeclaration":
            if (node.body.type === "BlockStatement")
              node.body.body.splice(0,0,node_increment_call)
            else {
              const singleBody = node.body;
              node.body = {
                type: "BlockStatement",
                body: [
                  node_increment_call,
                  singleBody
                ]
              }
            }
            break;
          case "ForInStatement":
          case "WhileStatement":
          case "ForStatement":
            if (node.body.type === "BlockStatement")
              node.body.body.splice(0,0,node_increment_loop)
            else {
              const singleBody = node.body;
              node.body = {
                type: "BlockStatement",
                body: [
                  node_increment_loop,
                  singleBody
                ]
              }
            }
            break;
          default:
            // console.log(node.type)
        }
    }});

    dataOut = escodegen.generate(ast)
    dataError = ""

    return [dataOut, dataError]
  }]
]

function handler(dataIn, args){
  let dataOut = "";
  let dataError = "";

  if (args.length === 0)
    dataError = "Error: no command line arguments specified"
  else{
    const commandIndex = commands.findIndex((v,i,arr) => v[0] === args[0]);

    if (commandIndex == -1)
      dataError = `Error: unknown command "${args[0]}"`
    else {
      const output = commands[commandIndex][1](dataIn, args);
      dataOut = output[0]
      dataError = output[1]
    }
  }

  return [dataOut, dataError]
}

const commandArgs = process.argv.slice(2);
try {
  const dataIn = fs.readFileSync('./in.txt', 'utf8');
  const handlerOutput = handler(dataIn, commandArgs)
  fs.writeFileSync('./out.txt', handlerOutput[0])
  fs.writeFileSync('./error.txt', handlerOutput[1])
} catch (err) {
  fs.writeFileSync('./error.txt', err.stack)
  fs.writeFileSync('./out.txt', "")
}