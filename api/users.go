package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"sync"

	"github.com/justingianelloni/jam/models"
)

type usersPage struct {
	Results    []models.User `json:"results"`
	TotalCount int           `json:"totalCount"`
}

func (c *Client) GetUser(ctx context.Context, usrID string) (*models.User, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/systemusers/"+usrID, nil)
	if err != nil {
		return nil, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API Error: %s", res.Status)
	}
	var user models.User
	if err := json.NewDecoder(res.Body).Decode(&user); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &user, nil
}

func (c *Client) listUsersPage(ctx context.Context, skip int, filters []models.V1Filter) (*usersPage, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	for i, f := range filters {
		params.Set(fmt.Sprintf("filter[%d]", i), f.String())
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/systemusers?"+params.Encode(), nil)
	if err != nil {
		return nil, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("Executing Request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API Error: %s", res.Status)
	}
	var users usersPage
	if err := json.NewDecoder(res.Body).Decode(&users); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &users, nil
}

func (c *Client) ListUsers(ctx context.Context, filters []models.V1Filter) ([]models.User, error) {
	first, err := c.listUsersPage(ctx, 0, filters)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	total := first.TotalCount
	users := make([]models.User, total)
	copy(users, first.Results)
	if len(first.Results) >= total {
		return users, nil
	}
	type result struct {
		skip  int
		users []models.User
		err   error
	}
	totalPages := (total + pageLimit - 1) / pageLimit
	results := make(chan result, totalPages-1)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, err := c.listUsersPage(ctx, skip, filters)
			if err != nil {
				results <- result{skip: skip, err: err}
				return
			}
			results <- result{skip: skip, users: page.Results}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(users[r.skip:], r.users)
	}
	return users, nil
}

type searchFilter struct {
	SearchTerm string   `json:"searchTerm"`
	Fields     []string `json:"fields"`
}

type searchBody struct {
	SearchFilter searchFilter `json:"searchFilter"`
}

func (c *Client) searchUsersPage(ctx context.Context, skip int, term string, fields []string) (*usersPage, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	body, err := json.Marshal(searchBody{SearchFilter: searchFilter{SearchTerm: term, Fields: fields}})
	if err != nil {
		return nil, fmt.Errorf("Encoding request body: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, baseURL+"/search/systemusers?"+params.Encode(), bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("Building request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API Error: %s", res.Status)
	}
	var users usersPage
	if err := json.NewDecoder(res.Body).Decode(&users); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &users, nil
}

func (c *Client) SearchUsers(ctx context.Context, term string, fields []string) ([]models.User, error) {
	first, err := c.searchUsersPage(ctx, 0, term, fields)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	total := first.TotalCount
	users := make([]models.User, total)
	copy(users, first.Results)
	if len(first.Results) >= total {
		return users, nil
	}
	type result struct {
		skip  int
		users []models.User
		err   error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, err := c.searchUsersPage(ctx, skip, term, fields)
			if err != nil {
				results <- result{skip: skip, err: err}
				return
			}
			results <- result{skip: skip, users: page.Results}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(users[r.skip:], r.users)
	}
	return users, nil
}

type boundSystem struct {
	ID string `json:"id"`
}

func (c *Client) boundSystemsPage(ctx context.Context, usrID string, skip int) ([]string, int, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v2/users/"+usrID+"/systems?"+params.Encode(), nil)
	if err != nil {
		return nil, 0, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, 0, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("API Error: %s", res.Status)
	}
	total, err := v2TotalCount(res)
	if err != nil {
		return nil, 0, fmt.Errorf("Fetching total count: %w", err)
	}
	var page []boundSystem
	if err := json.NewDecoder(res.Body).Decode(&page); err != nil {
		return nil, 0, fmt.Errorf("Decoding response: %w", err)
	}
	systems := make([]string, len(page))
	for i, s := range page {
		systems[i] = s.ID
	}
	return systems, total, nil
}

func (c *Client) ListBoundSystems(ctx context.Context, usrID string) ([]string, error) {
	first, total, err := c.boundSystemsPage(ctx, usrID, 0)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	systems := make([]string, total)
	copy(systems, first)
	if len(first) >= total {
		return systems, nil
	}
	type result struct {
		skip    int
		systems []string
		err     error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			systems, _, err := c.boundSystemsPage(ctx, usrID, skip)
			if err != nil {
				results <- result{skip: skip, err: err}
				return
			}
			results <- result{skip: skip, systems: systems}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(systems[r.skip:], r.systems)
	}
	return systems, nil
}
