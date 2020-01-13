#include "shape_fill_shader_shared"

in Vertex {
	VertexAttrs attrs;
} iVert;

out vec4 fragColor;
void main() {
	TDCheckDiscard();

	vec4 color = iVert.attrs.color;
	TDAlphaTest(color.a);
	fragColor = TDOutputSwizzle(color);
}

