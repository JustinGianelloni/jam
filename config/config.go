package config

import (
	"context"
	"fmt"

	op "github.com/1password/onepassword-sdk-go"
	"github.com/spf13/viper"
)

type Credentials struct {
	ClientID     string
	ClientSecret string
}

func Load(ctx context.Context) (*Credentials, error) {
	clientID := viper.GetString("JAM_CLIENT_ID")
	clientSecret := viper.GetString("JAM_CLIENT_SECRET")
	if clientID != "" && clientSecret != "" {
		return &Credentials{ClientID: clientID, ClientSecret: clientSecret}, nil
	}
	account := viper.GetString("OP_ACCOUNT")
	if account == "" {
		return nil, fmt.Errorf("JAM_CLIENT_ID/JAM_CLIENT_SECRET not set and OP_ACCOUNT not configured in config.json")
	}
	opClient, err := op.NewClient(ctx,
		op.WithDesktopAppIntegration(account),
		op.WithIntegrationInfo("jam", "v0.1.0"),
	)
	if err != nil {
		return nil, fmt.Errorf("connecting to 1Password: %w", err)
	}
	if clientID == "" {
		clientID, err = fetchClientID(ctx, opClient)
		if err != nil {
			return nil, fmt.Errorf("Error fetching Client ID from 1Password: %w", err)
		}
	}
	if clientSecret == "" {
		clientSecret, err = fetchClientSecret(ctx, opClient)
		if err != nil {
			return nil, fmt.Errorf("Error fetching Client Secret from 1Password: %w", err)
		}
	}
	return &Credentials{ClientID: clientID, ClientSecret: clientSecret}, nil
}

func fetchClientID(ctx context.Context, opClient *op.Client) (string, error) {
	uri := viper.GetString("OP_CLIENT_ID_URI")
	if uri == "" {
		return "", fmt.Errorf("JAM_CLIENT_ID not set and OP_CLIENT_ID_URI not configured in config.json")
	}
	clientID, err := opClient.Secrets().Resolve(ctx, uri)
	if err != nil {
		return "", fmt.Errorf("resolving OP_CLIENT_ID_URI: %w", err)
	}
	return clientID, nil
}

func fetchClientSecret(ctx context.Context, opClient *op.Client) (string, error) {
	uri := viper.GetString("OP_CLIENT_SECRET_URI")
	if uri == "" {
		return "", fmt.Errorf("JAM_CLIENT_SECRET not set and OP_CLIENT_SECRET_URI not configured in config.json")
	}
	clientSecret, err := opClient.Secrets().Resolve(ctx, uri)
	if err != nil {
		return "", fmt.Errorf("resolving OP_CLIENT_SECRET_URI: %w", err)
	}
	return clientSecret, nil
}
