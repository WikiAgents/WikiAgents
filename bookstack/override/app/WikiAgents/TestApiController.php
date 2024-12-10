<?php

namespace BookStack\WikiAgents;

use BookStack\Http\Controller;

use BookStack\Http\HttpRequestService;


class TestApiController extends Controller
{
    protected HttpRequestService $httpRequestService;

    // Inject HttpRequestService through the constructor
    public function __construct(HttpRequestService $httpRequestService)
    {
        $this->httpRequestService = $httpRequestService;
    }

    public function get(): string
    {
        // Build the client with a timeout of 5 seconds (or any desired timeout)
        $client = $this->httpRequestService->buildClient(5);

        // Create the JSON request for a GET request
        $request = $this->httpRequestService->jsonRequest('GET', 'http://api/test', []);

        try {
            // Send the request and capture the response
            $response = $client->send($request);

            // Return the response body as a string
            return (string) $response->getBody();
        } catch (RequestException $e) {
            // Handle errors (you can customize this further as needed)
            return "Error: " . $e->getMessage();
        }
    }

}
