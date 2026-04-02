package api

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"sync"

	"github.com/justingianelloni/jam/models"
)

type appPage struct {
	Results    []models.Application `json:"results"`
	TotalCount int                  `json:"totalCount"`
}

func (c *Client) listAppsPage(ctx context.Context, skip int, filters []models.V1Filter) (*appPage, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	for i, f := range filters {
		params.Set(fmt.Sprintf("filter[%d]", i), f.String())
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/applications?"+params.Encode(), nil)
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
	var apps appPage
	if err := json.NewDecoder(res.Body).Decode(&apps); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &apps, nil
}

func (c *Client) ListApps(ctx context.Context, filters []models.V1Filter) ([]models.Application, error) {
	first, err := c.listAppsPage(ctx, 0, filters)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	total := first.TotalCount
	apps := make([]models.Application, total)
	copy(apps, first.Results)
	if len(first.Results) >= total {
		return apps, nil
	}
	type result struct {
		skip int
		apps []models.Application
		err  error
	}
	totalPages := (total + pageLimit - 1) / pageLimit
	results := make(chan result, totalPages-1)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, err := c.listAppsPage(ctx, skip, filters)
			if err != nil {
				results <- result{skip: skip, err: err}
				return
			}
			results <- result{skip: skip, apps: page.Results}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(apps[r.skip:], r.apps)
	}
	return apps, nil
}

type group struct {
	ID string `json:"id"`
}

type groupResult struct {
	To group `json:"to"`
}

func (c *Client) appGroupsPage(ctx context.Context, appID string, skip int) ([]string, int, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	params.Set("targets", "user_group")
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v2/applications/"+appID+"/associations?"+params.Encode(), nil)
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
	var results []groupResult
	if err := json.NewDecoder(res.Body).Decode(&results); err != nil {
		return nil, 0, fmt.Errorf("Decoding Response: %w", err)
	}
	groups := make([]string, len(results))
	for i, g := range results {
		groups[i] = g.To.ID
	}
	return groups, total, nil
}

func (c *Client) ListAppGroups(ctx context.Context, appID string) ([]string, error) {
	first, total, err := c.appGroupsPage(ctx, appID, 0)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	groups := make([]string, total)
	copy(groups, first)
	if len(first) >= total {
		return groups, nil
	}
	type result struct {
		skip   int
		groups []string
		err    error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, _, err := c.appGroupsPage(ctx, appID, skip)
			if err != nil {
				results <- result{skip: skip, err: err}
				return
			}
			results <- result{skip: skip, groups: page}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(groups[r.skip:], r.groups)
	}
	return groups, nil
}
