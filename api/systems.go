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

func (c *Client) GetSystem(ctx context.Context, sysID string) (*models.System, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/systems/"+sysID, nil)
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
	var system models.System
	if err := json.NewDecoder(res.Body).Decode(&system); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &system, nil
}

type systemsPage struct {
	Results    []models.System `json:"results"`
	TotalCount int             `json:"totalCount"`
}

func (c *Client) listSystemsPage(ctx context.Context, skip int, filters []models.V1Filter) (*systemsPage, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	for i, f := range filters {
		params.Set(fmt.Sprintf("filter[%d]", i), f.String())
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/systems?"+params.Encode(), nil)
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
	var systems systemsPage
	if err := json.NewDecoder(res.Body).Decode(&systems); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &systems, nil
}

func (c *Client) ListSystems(ctx context.Context, filters []models.V1Filter) ([]models.System, error) {
	first, err := c.listSystemsPage(ctx, 0, filters)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	total := first.TotalCount
	systems := make([]models.System, total)
	copy(systems, first.Results)
	if len(first.Results) >= total {
		return systems, nil
	}
	type result struct {
		skip    int
		systems []models.System
		err     error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, err := c.listSystemsPage(ctx, skip, filters)
			if err != nil {
				results <- result{skip: skip, err: err}
			}
			results <- result{skip: skip, systems: page.Results}
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

func (c *Client) searchSystemsPage(ctx context.Context, skip int, term string, fields []string) (*systemsPage, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	body, err := json.Marshal(searchBody{SearchFilter: searchFilter{SearchTerm: term, Fields: fields}})
	if err != nil {
		return nil, fmt.Errorf("Encoding request body: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, baseURL+"/search/systems?"+params.Encode(), bytes.NewReader(body))
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
	var systems systemsPage
	if err := json.NewDecoder(res.Body).Decode(&systems); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &systems, nil
}

func (c *Client) SearchSystems(ctx context.Context, term string, fields []string) ([]models.System, error) {
	first, err := c.searchSystemsPage(ctx, 0, term, fields)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	total := first.TotalCount
	systems := make([]models.System, total)
	copy(systems, first.Results)
	if len(first.Results) >= total {
		return systems, nil
	}
	type result struct {
		skip    int
		systems []models.System
		err     error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, err := c.searchSystemsPage(ctx, skip, term, fields)
			if err != nil {
				results <- result{skip: skip, err: err}
			}
			results <- result{skip: skip, systems: page.Results}
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

type boundUser struct {
	ID string `json:"id"`
}

func (c *Client) boundUsersPage(ctx context.Context, sysID string, skip int) ([]string, int, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v2/systems/"+sysID+"/users?"+params.Encode(), nil)
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
	var page []boundUser
	if err := json.NewDecoder(res.Body).Decode(&page); err != nil {
		return nil, 0, fmt.Errorf("Decoding response: %w", err)
	}
	users := make([]string, len(page))
	for i, u := range page {
		users[i] = u.ID
	}
	return users, total, nil
}

func (c *Client) ListBoundUsers(ctx context.Context, sysID string) ([]string, error) {
	first, total, err := c.boundUsersPage(ctx, sysID, 0)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	users := make([]string, total)
	copy(users, first)
	if len(first) >= total {
		return users, nil
	}
	type result struct {
		skip  int
		users []string
		err   error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, _, err := c.boundUsersPage(ctx, sysID, skip)
			if err != nil {
				results <- result{skip: skip, err: err}
			}
			results <- result{skip: skip, users: page}
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
