#include "shape_shader_shared"

uniform sampler2D sAppearanceData;
uniform sampler2D sLocalData;
uniform sampler2D sGlobalData;

in int shapeIndex;
in vec3 centerPos;
in vec3 rotateAxis;

out Vertex {
	VertexAttrs attrs;
} oVert;

Appearance loadAppearance() {
	Appearance data;
	data.color = texelFetch(sAppearanceData, ivec2(shapeIndex, 0), 0);
	vec4 opacityTexOpacitySourceMode = texelFetch(sAppearanceData, ivec2(shapeIndex, 1), 0);
	data.opacity = opacityTexOpacitySourceMode.r;
	data.texOpacity = opacityTexOpacitySourceMode.g;
	data.texSource = int(opacityTexOpacitySourceMode.b);
	data.texUVMode = int(opacityTexOpacitySourceMode.a);
	data.texOffset = texelFetch(sAppearanceData, ivec2(shapeIndex, 2), 0).rgb;
	vec2 texRotateScale = texelFetch(sAppearanceData, ivec2(shapeIndex, 3), 0).rg;
	data.texRotate = texRotateScale.r;
	data.texScale = texRotateScale.g;
	return data;
}

Transform loadTransform(sampler2D sampler) {
	Transform data;
	data.translate = texelFetch(sampler, ivec2(shapeIndex, 0), 0).rgb;
	data.rotate = texelFetch(sampler, ivec2(shapeIndex, 1), 0).rgb;
	data.scale = texelFetch(sampler, ivec2(shapeIndex, 2), 0).rgb;
	data.pivot = texelFetch(sampler, ivec2(shapeIndex, 3), 0).rgb;
	return data;
}

void main() {
	#ifndef TD_PICKING_ACTIVE

	oVert.attrs.appearance = loadAppearance();
	Transform localTransform = loadTransform(sLocalData);
	Transform globalTransform = loadTransform(sGlobalData);

	vec4 worldSpacePos = TDDeform(P);
	gl_Position = TDWorldToProj(worldSpacePos);

	#else

	TDWritePickingValues();

	#endif
}


