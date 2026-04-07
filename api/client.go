package api

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/justingianelloni/jam/internal/config"
)

const (
	baseURL     = "https://console.jumpcloud.com/api"
	OAuthURL    = "https://admin-oauth.id.jumpcloud.com/oauth2/token"
	pageLimit   = 100
	tokenBuffer = 30 * time.Second
	timeout     = 30 * time.Second
)

type Client struct {
	clientID     string
	clientSecret string
	httpClient   *http.Client
	mu           sync.Mutex
	token        string
	expiration   time.Time
}

type tokenResponse struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	ExpiresIn   int    `json:"expires_in"`
}

func (c *Client) accessToken(ctx context.Context) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.token != "" && time.Now().Add(tokenBuffer).Before(c.expiration) {
		return c.token, nil
	}
	creds := base64.StdEncoding.EncodeToString([]byte(c.clientID + ":" + c.clientSecret))
	body := url.Values{}
	body.Set("grant_type", "client_credentials")
	body.Set("scope", "api")
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, OAuthURL, strings.NewReader(body.Encode()))
	if err != nil {
		return "", fmt.Errorf("Building token request: %w", err)
	}
	req.Header.Set("Authorization", "Basic "+creds)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	res, err := c.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("Fetching token: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Token endpoint return status %d", res.StatusCode)
	}
	var tr tokenResponse
	if err := json.NewDecoder(res.Body).Decode(&tr); err != nil {
		return "", fmt.Errorf("Decoding token response: %w", err)
	}
	c.token = tr.AccessToken
	c.expiration = time.Now().Add(time.Duration(tr.ExpiresIn) * time.Second)
	return c.token, nil
}

func (c *Client) do(ctx context.Context, req *http.Request) (*http.Response, error) {
	token, err := c.accessToken(ctx)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Accept", "application/json")
	return c.httpClient.Do(req)
}

func v2TotalCount(res *http.Response) (int, error) {
	total, err := strconv.Atoi(res.Header.Get("X-Total-Count"))
	if err != nil {
		return 0, fmt.Errorf("Parsing X-Total-Count: %w", err)
	}
	return total, nil
}

func NewClient(creds *config.Credentials) *Client {
	return &Client{
		clientID:     creds.ClientID,
		clientSecret: creds.ClientSecret,
		httpClient:   &http.Client{Timeout: timeout},
	}
}
