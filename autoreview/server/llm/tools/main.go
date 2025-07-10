package tools

import (
	"fmt"
	"reflect"

	"github.com/liushuangls/go-anthropic/v2"
	"github.com/liushuangls/go-anthropic/v2/jsonschema"
)

type Tool interface {
	Name() string
	Description() string
	GenerateCommand(content []byte) ([]string, error)
}

func GetToolDefinition(t Tool) anthropic.ToolDefinition {
	inputs := map[string]jsonschema.Definition{}
	inputNames := []string{}
	toolType := reflect.TypeOf(t)
	for i := range toolType.NumField() {
		f := toolType.Field(i)
		fName := f.Tag.Get("json")
		inputNames = append(inputNames, fName)
		if f.Type.Kind() == reflect.Int {
			inputs[fName] = jsonschema.Definition{
				Type:        jsonschema.Number,
				Description: fName,
			}
		} else if f.Type.Kind() == reflect.String {
			inputs[fName] = jsonschema.Definition{
				Type:        jsonschema.String,
				Description: fName,
			}
		} else {
			panic(fmt.Sprintf("Cannot handle type %+v for field %v", f.Type.Kind(), fName))
		}
	}

	return anthropic.ToolDefinition{
		Name:        t.Name(),
		Description: t.Description(),
		InputSchema: jsonschema.Definition{
			Type:       jsonschema.Object,
			Properties: inputs,
			Required:   inputNames,
		},
		CacheControl: &anthropic.MessageCacheControl{
			Type: anthropic.CacheControlTypeEphemeral,
		},
	}
}
