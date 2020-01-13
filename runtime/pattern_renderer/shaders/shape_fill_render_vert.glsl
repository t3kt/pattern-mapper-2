#include "shape_fill_shader_shared"

out Vertex {
	VertexAttrs attrs;
} oVert;

void main() {
	#ifndef TD_PICKING_ACTIVE

	vec4 worldSpacePos = TDDeform(P);
	gl_Position = TDWorldToProj(worldSpacePos);

	#else

	TDWritePickingValues();

	#endif
}


