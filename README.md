# tech-challenge-2

```mermaid
flowchart TD
    Client[Client / Browser] -->|HTTP/HTTPS| App[App in Public Subnet]
    App -->|DB Connection| DB[RDS in Private Subnet]

    subgraph PublicSubnet["Public Subnet"]
        App
        IGW[Internet Gateway]
    end

    subgraph PrivateSubnet["Private Subnet"]
        DB
        NAT[NAT Gateway (optional)]
    end

    App --> IGW
    DB -->|Outbound Internet (optional)| NAT --> IGW

    %% Security Groups
    App -->|Outbound to DB port| DB
```