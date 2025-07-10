#include "Graphs/SVFG.h"
#include "SVF-LLVM/SVFIRBuilder.h"
#include "Util/Options.h"
#include "WPA/Andersen.h"
#include "SVFIR/SVFVariables.h"

#include <unordered_set>

int main(int argc, char **argv) {

  std::vector<std::string> moduleNameVec =
      OptionBase::parseOptions(argc, argv, "Whole Program Points-to Analysis",
                               "[options] <input-bitcode...>");

  if (SVF::Options::WriteAnder() == "ir_annotator") {
    SVF::LLVMModuleSet::preProcessBCs(moduleNameVec);
  }

  SVF::LLVMModuleSet::buildSVFModule(moduleNameVec);

  /// Build Program Assignment Graph (SVFIR)
  SVF::SVFIRBuilder builder;
  SVF::SVFIR *pag = builder.build();
  std::unordered_set<SVF::NodeID> allowed;
  SVF::NodeID hello_arg = 0;
  for (auto& [id, var] : *pag)
  {
    if (SVF::SVFUtil::isa<SVF::ArgValVar>(var))
    {
      const SVF::ArgValVar* arg = SVF::SVFUtil::cast<SVF::ArgValVar>(var);
      const SVF::FunObjVar* callee = arg->getParent();
      if (arg->getArgNo() == 0 && callee != nullptr && callee->getName() == "say_hello")
      {
        if (hello_arg != 0 || id == 0) return -1;
        hello_arg = id;
      }
    }
    else if (SVF::SVFUtil::isa<SVF::GlobalObjVar>(var))
    {
      const SVF::GlobalObjVar* global = SVF::SVFUtil::cast<SVF::GlobalObjVar>(var);
      if (global->getValueName().find("flag") == std::string::npos)
        allowed.insert(id);
    }
  }
  if (hello_arg == 0) return -1;
  llvm::errs() << "Hello Argument ID: " << hello_arg  << '\n';

  SVF::Andersen *ander = SVF::AndersenWaveDiff::createAndersenWaveDiff(pag);

  for (auto n : ander->getPts(hello_arg))
  {
    if (allowed.count(n) == 0)
    {
      llvm::errs() << "Points-to node " << n << " not allowed!\n";
      return -1;
    }
  }

  SVF::AndersenWaveDiff::releaseAndersenWaveDiff();
  SVF::SVFIR::releaseSVFIR();

  SVF::LLVMModuleSet::releaseLLVMModuleSet();

  llvm::llvm_shutdown();
  return 0;
}