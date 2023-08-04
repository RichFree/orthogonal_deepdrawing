#include <iostream>
#include <fstream>
#include <string>
#include <ogdf/fileformats/GraphIO.h>
#include <ogdf/orthogonal/OrthoLayout.h>
#include <ogdf/planarity/EmbedderMinDepthMaxFaceLayers.h>
#include <ogdf/planarity/PlanarSubgraphFast.h>
#include <ogdf/planarity/PlanarSubgraphPC.h>
#include <ogdf/planarity/PlanarizationLayout.h>
#include <ogdf/planarity/SubgraphPlanarizer.h>
// #include <ogdf/planarity/VariableEmbeddingInserter.h>
#include <ogdf/planarity/FixedEmbeddingInserter.h>
#include <ogdf/basic/GraphAttributes.h>

#include <getopt.h>
// requires C++17
#include <filesystem>


using namespace ogdf;
 
int main(int argc, char* argv[])
{
    // duration
    // time_point<high_resolution_clock> start, end;
    // start = high_resolution_clock::now();


    // stod -> string to double
    string input_file = argv[1];

    Graph G;
 

    // read gml
    if (!GraphIO::read(G, input_file, GraphIO::readGML)) {
        std::cerr << "Could not read input.gml" << std::endl;
        return 1;
    }
 
    GraphAttributes GA(G);

    // convert each node into a point
    for (node v : G.nodes)
    {
        GA.width(v) = 0.1;
        GA.height(v) = 0.1;
    }
 
    PlanarizationLayout pl;
 
    SubgraphPlanarizer *crossMin = new SubgraphPlanarizer;

    // PQ tree implementation
    // PlanarSubgraphFast<int> *ps = new PlanarSubgraphFast<int>;
    
    // PC tree implementation
    PlanarSubgraphPC<int> *ps = new PlanarSubgraphPC<int>;
    ps->runs(0);


    // Fixed insertion 
    FixedEmbeddingInserter *fix = new FixedEmbeddingInserter;

    // variable insertion 
    // VariableEmbeddingInserter *ves = new VariableEmbeddingInserter;
    // ves->removeReinsert(RemoveReinsertType::All);
 
    crossMin->setSubgraph(ps);
    crossMin->setInserter(fix);
    pl.setCrossMin(crossMin);
 
    EmbedderMinDepthMaxFaceLayers *emb = new EmbedderMinDepthMaxFaceLayers;
    pl.setEmbedder(emb);

 
    OrthoLayout *ol = new OrthoLayout;
    // original: 20.0
    double sep_parameter = 20.0;
    ol->separation(sep_parameter);
    // original: 0.4
    double cOver_parameter = 0.4;
    ol->cOverhang(cOver_parameter);
    ol->scaling(1);
    pl.setPlanarLayouter(ol);
 
    pl.call(GA);
 
    std::filesystem::path p = input_file;
    string filename = p.filename().replace_extension().string();

    GraphIO::write(GA, "output_" + filename + ".gml", GraphIO::writeGML);
    GraphIO::write(GA, "output_" + filename + ".svg", GraphIO::drawSVG);

    // get bounding box
    // DRect bb = GA.boundingBox();
    // std::cout << filename << ", " << bb.height() << ", " << bb.width() << std::endl;


    return 0;
}
