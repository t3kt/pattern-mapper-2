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
	return data;
}

UVAttrs loadUVAttrs() {
	UVAttrs data;
	vec4 opacityTexOpacitySourceMode = texelFetch(sAppearanceData, ivec2(shapeIndex, 1), 0);
	data.uvMode = int(opacityTexOpacitySourceMode.a);
	data.offset = texelFetch(sAppearanceData, ivec2(shapeIndex, 2), 0).rgb;
	vec2 texRotateScale = texelFetch(sAppearanceData, ivec2(shapeIndex, 3), 0).rg;
	data.rotate = texRotateScale.r;
	data.scale = texRotateScale.g;
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

vec3 getTexCoord(int uvMode) {
	switch (uvMode) {
		case UVMODE_LOCAL: return uv[2];
		case UVMODE_GLOBAL: return uv[1];
		case UVMODE_PATH: return uv[0];
		default: return vec3(0);
	}
}

void main() {
	#ifndef TD_PICKING_ACTIVE

	oVert.attrs.appearance = loadAppearance();
	oVert.attrs.color = Cd;

	Transform localTransform = loadTransform(sLocalData);
	localTransform.pivot += centerPos;
	Transform globalTransform = loadTransform(sGlobalData);

	UVAttrs uvAttrs = loadUVAttrs();
	vec4 texCoord = vec4(getTexCoord(uvAttrs.uvMode), 0);
	scaleRotateTranslate(
		texCoord,
		vec3(uvAttrs.scale),
		vec3(0, 0, uvAttrs.rotate),
		uvAttrs.offset,
		vec3(0.5),
		vec3(0));
	oVert.attrs.texCoord = texCoord.xyz;

	vec4 worldSpacePos = TDDeform(P);

	applyTransform(worldSpacePos, localTransform, rotateAxis);
	applyTransform(worldSpacePos, globalTransform, vec3(0));

	gl_Position = TDWorldToProj(worldSpacePos);

	#else

	TDWritePickingValues();

	#endif
}


