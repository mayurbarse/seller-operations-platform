
import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  LayoutDashboard,
  Store,
  ShoppingCart,
  Truck,
  AlertTriangle,
  Wallet,
  Star,
  RefreshCw,
  TrendingUp,
  Activity,
  Package,
} from 'lucide-react'
import './App.css'

const API = 'http://127.0.0.1:8000'

const currency = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)

const number = (value) =>
  new Intl.NumberFormat('en-IN').format(Number(value) || 0)

const formatDate = (value) => {
  if (!value) return 'N/A'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return 'N/A'

  return date.toLocaleString('en-IN')
}

function StatCard({ title, value, subtitle, icon: Icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <div className="stat-icon">
          <Icon size={19} />
        </div>
      </div>
      <h2>{value}</h2>
      <p>{subtitle}</p>
    </div>
  )
}

function App() {
  // Dashboard state
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [apiConnected, setApiConnected] = useState(false)

  // Navigation
  const [activePage, setActivePage] = useState('Overview')

  // Sellers
  const [sellerData, setSellerData] = useState([])
  const [sellerLoading, setSellerLoading] = useState(false)
  const [sellerError, setSellerError] = useState('')
  const [sellerSearch, setSellerSearch] = useState('')
  const [sellerStatus, setSellerStatus] = useState('all')
  const [sellerRisk, setSellerRisk] = useState('all')
  const [sellerOffset, setSellerOffset] = useState(0)
  const [sellerTotal, setSellerTotal] = useState(0)
  const sellerLimit = 50

  // Orders
  const [orders, setOrders] = useState([])
  const [ordersTotal, setOrdersTotal] = useState(0)
  const [ordersLoading, setOrdersLoading] = useState(false)
  const [ordersError, setOrdersError] = useState('')
  const [orderSearch, setOrderSearch] = useState('')
  const [orderStatus, setOrderStatus] = useState('all')
  const [orderOffset, setOrderOffset] = useState(0)
  const orderLimit = 50

  // Fulfillment
  const [fulfillments, setFulfillments] = useState([])
  const [fulfillmentTotal, setFulfillmentTotal] = useState(0)
  const [fulfillmentLoading, setFulfillmentLoading] = useState(false)
  const [fulfillmentError, setFulfillmentError] = useState('')
  const [fulfillmentSearch, setFulfillmentSearch] = useState('')
  const [fulfillmentStatus, setFulfillmentStatus] = useState('all')
  const [fulfillmentOffset, setFulfillmentOffset] = useState(0)
  const fulfillmentLimit = 50

  // Disputes
  const [disputes, setDisputes] = useState([])
  const [disputesTotal, setDisputesTotal] = useState(0)
  const [disputesLoading, setDisputesLoading] = useState(false)
  const [disputesError, setDisputesError] = useState('')
  const [disputeSearch, setDisputeSearch] = useState('')
  const [disputeStatus, setDisputeStatus] = useState('all')
  const [disputeOffset, setDisputeOffset] = useState(0)
  const disputeLimit = 50

  // Payouts
  const [payouts, setPayouts] = useState([])
  const [payoutsTotal, setPayoutsTotal] = useState(0)
  const [payoutsLoading, setPayoutsLoading] = useState(false)
  const [payoutsError, setPayoutsError] = useState('')
  const [payoutSearch, setPayoutSearch] = useState('')
  const [payoutStatus, setPayoutStatus] = useState('all')
  const [payoutOffset, setPayoutOffset] = useState(0)
  const payoutLimit = 50

  // Load dashboard
  const loadDashboard = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await axios.get(`${API}/analytics/dashboard`)

      setData(response.data)
      setApiConnected(true)
    } catch (err) {
      setApiConnected(false)
      setError(
        err.response?.data?.detail ||
          'Could not connect to the backend. Check that FastAPI is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  // Load sellers
  const loadSellers = async () => {
    try {
      setSellerLoading(true)
      setSellerError('')

      const response = await axios.get(`${API}/analytics/sellers`, {
        params: {
          limit: sellerLimit,
          offset: sellerOffset,
        },
      })

      setSellerData(response.data.sellers || [])
      setSellerTotal(response.data.total || 0)
      setApiConnected(true)
    } catch (err) {
      setSellerError(
        err.response?.data?.detail ||
          'Could not load seller records. Check that the backend is running.'
      )
      setApiConnected(false)
    } finally {
      setSellerLoading(false)
    }
  }

  // Load orders
  const loadOrders = async () => {
    try {
      setOrdersLoading(true)
      setOrdersError('')

      const params = {
        limit: orderLimit,
        offset: orderOffset,
      }

      if (orderStatus !== 'all') {
        params.status = orderStatus
      }

      const response = await axios.get(`${API}/orders`, { params })

      setOrders(response.data.orders || [])
      setOrdersTotal(response.data.total || 0)
      setApiConnected(true)
    } catch (err) {
      setOrdersError(
        err.response?.data?.detail ||
          'Could not load order records. Check that the backend is running.'
      )
      setApiConnected(false)
    } finally {
      setOrdersLoading(false)
    }
  }

  // Load fulfillment records
  const loadFulfillments = async () => {
    try {
      setFulfillmentLoading(true)
      setFulfillmentError('')

      const params = {
        limit: fulfillmentLimit,
        offset: fulfillmentOffset,
      }

      if (fulfillmentStatus !== 'all') {
        params.status = fulfillmentStatus
      }

      const response = await axios.get(`${API}/fulfillments`, { params })

      setFulfillments(response.data.fulfillments || [])
      setFulfillmentTotal(response.data.total || 0)
      setApiConnected(true)
    } catch (err) {
      setFulfillmentError(
        err.response?.data?.detail ||
          'Could not load fulfillment records. Check that the backend is running.'
      )
      setApiConnected(false)
    } finally {
      setFulfillmentLoading(false)
    }
  }

  // Load dispute records
  const loadDisputes = async () => {
    try {
      setDisputesLoading(true)
      setDisputesError('')

      const params = {
        limit: disputeLimit,
        offset: disputeOffset,
      }

      if (disputeStatus !== 'all') {
        params.status = disputeStatus
      }

      const response = await axios.get(`${API}/disputes`, { params })

      setDisputes(response.data.disputes || [])
      setDisputesTotal(response.data.total || 0)
      setApiConnected(true)
    } catch (err) {
      setDisputesError(
        err.response?.data?.detail ||
          'Could not load dispute records. Check that the backend is running.'
      )
      setApiConnected(false)
    } finally {
      setDisputesLoading(false)
    }
  }

  // Load payout records
  const loadPayouts = async () => {
    try {
      setPayoutsLoading(true)
      setPayoutsError('')

      const params = {
        limit: payoutLimit,
        offset: payoutOffset,
      }

      if (payoutStatus !== 'all') {
        params.status = payoutStatus
      }

      const response = await axios.get(`${API}/payouts`, { params })

      setPayouts(response.data.payouts || [])
      setPayoutsTotal(response.data.total || 0)
      setApiConnected(true)
    } catch (err) {
      setPayoutsError(
        err.response?.data?.detail ||
          'Could not load payout records. Check that the backend is running.'
      )
      setApiConnected(false)
    } finally {
      setPayoutsLoading(false)
    }
  }

 
  // Initial dashboard loading
  useEffect(() => {
    const task = Promise.resolve().then(() => loadDashboard())
    return () => {
      task.catch(() => {})
    }
   
  }, [])

  // Load sellers when required
  useEffect(() => {
    if (activePage === 'Sellers') {
      Promise.resolve().then(() => loadSellers())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, sellerOffset])

  // Load orders when required
  useEffect(() => {
    if (activePage === 'Orders') {
      Promise.resolve().then(() => loadOrders())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, orderOffset, orderStatus])

  // Load fulfillment when required
  useEffect(() => {
    if (activePage === 'Fulfillment') {
      Promise.resolve().then(() => loadFulfillments())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, fulfillmentOffset, fulfillmentStatus])

  // Load disputes when required
  useEffect(() => {
    if (activePage === 'Disputes') {
      Promise.resolve().then(() => loadDisputes())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, disputeOffset, disputeStatus])

  // Load payouts when required
  useEffect(() => {
    if (activePage === 'Payouts') {
      Promise.resolve().then(() => loadPayouts())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, payoutOffset, payoutStatus])


  // Sidebar menu
  const menu = [
    { name: 'Overview', icon: LayoutDashboard },
    { name: 'Sellers', icon: Store },
    { name: 'Orders', icon: ShoppingCart },
    { name: 'Fulfillment', icon: Truck },
    { name: 'Disputes', icon: AlertTriangle },
    { name: 'Payouts', icon: Wallet },
  ]

  // Filter sellers on current page
  const filteredSellers = sellerData.filter((seller) => {
    const search = sellerSearch.toLowerCase()

    const matchesSearch =
      (seller.seller_id || '').toLowerCase().includes(search) ||
      (seller.seller_name || '').toLowerCase().includes(search)

    const matchesStatus =
      sellerStatus === 'all' || seller.status === sellerStatus

    const matchesRisk =
      sellerRisk === 'all' || seller.risk_level === sellerRisk

    return matchesSearch && matchesStatus && matchesRisk
  })

  // Filter orders on current page
  const filteredOrders = orders.filter((order) => {
    const search = orderSearch.toLowerCase()

    return (
      (order.order_id || '').toLowerCase().includes(search) ||
      (order.customer_id || '').toLowerCase().includes(search)
    )
  })

  // Filter fulfillment records on current page
  const filteredFulfillments = fulfillments.filter((item) => {
    const search = fulfillmentSearch.toLowerCase()

    return (
      (item.fulfillment_id || '').toLowerCase().includes(search) ||
      (item.order_line_id || '').toLowerCase().includes(search) ||
      (item.seller_id || '').toLowerCase().includes(search) ||
      (item.tracking_code || '').toLowerCase().includes(search) ||
      (item.carrier || '').toLowerCase().includes(search)
    )
  })

  // Filter disputes on current page
  const filteredDisputes = disputes.filter((item) => {
    const search = disputeSearch.toLowerCase()

    return (
      (item.dispute_id || '').toLowerCase().includes(search) ||
      (item.order_id || '').toLowerCase().includes(search) ||
      (item.order_line_id || '').toLowerCase().includes(search) ||
      (item.seller_id || '').toLowerCase().includes(search) ||
      (item.reason || '').toLowerCase().includes(search)
    )
  })

  // Filter payouts on current page
  const filteredPayouts = payouts.filter((item) => {
    const search = payoutSearch.toLowerCase()

    return (
      (item.payout_id || '').toLowerCase().includes(search) ||
      (item.seller_id || '').toLowerCase().includes(search) ||
      (item.status || '').toLowerCase().includes(search)
    )
  })

  // Refresh selected page
  const handleRefresh = () => {
    if (activePage === 'Sellers') {
      loadSellers()
    } else if (activePage === 'Orders') {
      loadOrders()
    } else if (activePage === 'Fulfillment') {
      loadFulfillments()
    } else if (activePage === 'Disputes') {
      loadDisputes()
    } else if (activePage === 'Payouts') {
      loadPayouts()
    } else if (activePage === 'Overview') {
      loadDashboard()
    }
  }

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">S</div>
          <div>
            <h2>SellerOps</h2>
            <span>Operations Platform</span>
          </div>
        </div>

        <div className="menu-label">WORKSPACE</div>

        <nav>
          {menu.map((item) => (
            <div
              className={`nav-item ${
                activePage === item.name ? 'active' : ''
              }`}
              key={item.name}
              onClick={() => setActivePage(item.name)}
              style={{ cursor: 'pointer' }}
            >
              <item.icon size={18} />
              <span>{item.name}</span>
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span
              className="status-dot"
              style={{
                backgroundColor: apiConnected ? '#22c55e' : '#ef4444',
              }}
            />
            <div>
              <strong>
                {apiConnected ? 'System operational' : 'API disconnected'}
              </strong>
              <small>
                {apiConnected ? 'Backend connected' : 'Check FastAPI server'}
              </small>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">
              Workspace / {activePage}
            </span>

            <h1>
              {activePage === 'Overview'
                ? 'Operations Dashboard'
                : `${activePage} Management`}
            </h1>
          </div>

          <button className="refresh-btn" onClick={handleRefresh}>
            <RefreshCw size={16} />
            Refresh data
          </button>
        </header>

        {/* Dashboard messages */}
        {activePage === 'Overview' && loading && (
          <div className="message">Loading dashboard data...</div>
        )}

        {activePage === 'Overview' && error && (
          <div className="error-message">
            {error}
            <button onClick={loadDashboard}>Retry</button>
          </div>
        )}

        {/* SELLERS MANAGEMENT */}
        {activePage === 'Sellers' && (
          <section className="sellers-page">
            <div className="welcome-row">
              <div>
                <h2>Seller Management</h2>
                <p>
                  Monitor seller accounts, performance and operational risk.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </div>

            <div className="seller-summary-grid">
              <div className="panel">
                <p>Total sellers</p>
                <h2>{number(sellerTotal)}</h2>
              </div>

              <div className="panel">
                <p>Sellers on this page</p>
                <h2>{number(sellerData.length)}</h2>
              </div>

              <div className="panel">
                <p>High-risk sellers on this page</p>
                <h2>
                  {number(
                    sellerData.filter(
                      (seller) => seller.risk_level === 'high'
                    ).length
                  )}
                </h2>
              </div>
            </div>

            <div className="panel seller-table-panel">
              <div className="seller-toolbar">
                <input
                  type="text"
                  placeholder="Search seller ID or name..."
                  value={sellerSearch}
                  onChange={(e) => setSellerSearch(e.target.value)}
                />

                <select
                  value={sellerStatus}
                  onChange={(e) => setSellerStatus(e.target.value)}
                >
                  <option value="all">All statuses</option>
                  <option value="active">Active</option>
                  <option value="suspended">Suspended</option>
                  <option value="inactive">Inactive</option>
                </select>

                <select
                  value={sellerRisk}
                  onChange={(e) => setSellerRisk(e.target.value)}
                >
                  <option value="all">All risk levels</option>
                  <option value="low">Low risk</option>
                  <option value="medium">Medium risk</option>
                  <option value="high">High risk</option>
                </select>
              </div>

              {sellerLoading && (
                <div className="message">Loading seller records...</div>
              )}

              {sellerError && (
                <div className="error-message">
                  {sellerError}
                  <button onClick={loadSellers}>Retry</button>
                </div>
              )}

              {!sellerLoading && !sellerError && (
                <>
                  <div className="table-wrapper">
                    <table className="seller-table">
                      <thead>
                        <tr>
                          <th>Seller</th>
                          <th>Status</th>
                          <th>Rating</th>
                          <th>Orders</th>
                          <th>GMV</th>
                          <th>Delivery</th>
                          <th>Disputes</th>
                          <th>Performance</th>
                          <th>Risk</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredSellers.map((seller) => (
                          <tr key={seller.seller_id}>
                            <td>
                              <strong>{seller.seller_name}</strong>
                              <small>{seller.seller_id}</small>
                            </td>

                            <td>
                              <span className={`status-badge ${seller.status}`}>
                                {seller.status}
                              </span>
                            </td>

                            <td>
                              <span className="rating-cell">
                                <Star size={14} />
                                {seller.seller_rating ?? 'N/A'}
                              </span>
                            </td>

                            <td>{number(seller.total_orders)}</td>
                            <td>{currency(seller.gmv)}</td>
                            <td>{seller.delivery_rate_percent ?? 0}%</td>
                            <td>{number(seller.total_disputes)}</td>

                            <td>
                              <strong>{seller.performance_score ?? 0}</strong>
                            </td>

                            <td>
                              <span className={`risk-badge ${seller.risk_level}`}>
                                {seller.risk_level}
                              </span>
                            </td>
                          </tr>
                        ))}

                        {filteredSellers.length === 0 && (
                          <tr>
                            <td colSpan="9" className="empty-table">
                              No matching sellers found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination">
                    <span>
                      Showing {sellerTotal === 0 ? 0 : sellerOffset + 1}–
                      {Math.min(sellerOffset + sellerLimit, sellerTotal)}
                      {' '}of {number(sellerTotal)} sellers
                    </span>

                    <div>
                      <button
                        disabled={sellerOffset === 0}
                        onClick={() =>
                          setSellerOffset(Math.max(0, sellerOffset - sellerLimit))
                        }
                      >
                        Previous
                      </button>

                      <button
                        disabled={sellerOffset + sellerLimit >= sellerTotal}
                        onClick={() => setSellerOffset(sellerOffset + sellerLimit)}
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* ORDERS MANAGEMENT */}
        {activePage === 'Orders' && (
          <section className="orders-page">
            <div className="welcome-row">
              <div>
                <h2>Orders Management</h2>
                <p>
                  Monitor customer orders, order values and processing status.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </div>

            <div className="order-summary-grid">
              <div className="panel">
                <p>Total orders matching filter</p>
                <h2>{number(ordersTotal)}</h2>
              </div>

              <div className="panel">
                <p>Orders on this page</p>
                <h2>{number(orders.length)}</h2>
              </div>

              <div className="panel">
                <p>Value on this page</p>
                <h2>
                  {currency(
                    orders.reduce(
                      (sum, order) => sum + Number(order.total_amount || 0),
                      0
                    )
                  )}
                </h2>
              </div>
            </div>

            <div className="panel order-table-panel">
              <div className="order-toolbar">
                <input
                  type="text"
                  placeholder="Search order ID or customer ID..."
                  value={orderSearch}
                  onChange={(e) => setOrderSearch(e.target.value)}
                />

                <select
                  value={orderStatus}
                  onChange={(e) => {
                    setOrderStatus(e.target.value)
                    setOrderOffset(0)
                  }}
                >
                  <option value="all">All statuses</option>
                  <option value="processing">Processing</option>
                  <option value="delivered">Delivered</option>
                  <option value="shipped">Shipped</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="returned">Returned</option>
                </select>
              </div>

              {ordersLoading && (
                <div className="message">Loading orders...</div>
              )}

              {ordersError && (
                <div className="error-message">
                  {ordersError}
                  <button onClick={loadOrders}>Retry</button>
                </div>
              )}

              {!ordersLoading && !ordersError && (
                <>
                  <div className="table-wrapper">
                    <table className="order-table">
                      <thead>
                        <tr>
                          <th>Order ID</th>
                          <th>Customer ID</th>
                          <th>Order Date</th>
                          <th>Amount</th>
                          <th>Currency</th>
                          <th>Status</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredOrders.map((order) => (
                          <tr key={order.order_id}>
                            <td><strong>{order.order_id}</strong></td>
                            <td>{order.customer_id}</td>
                            <td>{formatDate(order.order_date)}</td>
                            <td><strong>{currency(order.total_amount)}</strong></td>
                            <td>{order.currency}</td>
                            <td>
                              <span className={`order-status ${order.status}`}>
                                {order.status}
                              </span>
                            </td>
                          </tr>
                        ))}

                        {filteredOrders.length === 0 && (
                          <tr>
                            <td colSpan="6" className="empty-table">
                              No matching orders found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination">
                    <span>
                      Showing {ordersTotal === 0 ? 0 : orderOffset + 1}–
                      {Math.min(orderOffset + orderLimit, ordersTotal)}
                      {' '}of {number(ordersTotal)} orders
                    </span>

                    <div>
                      <button
                        disabled={orderOffset === 0}
                        onClick={() =>
                          setOrderOffset(Math.max(0, orderOffset - orderLimit))
                        }
                      >
                        Previous
                      </button>

                      <button
                        disabled={orderOffset + orderLimit >= ordersTotal}
                        onClick={() => setOrderOffset(orderOffset + orderLimit)}
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* FULFILLMENT MANAGEMENT */}
        {activePage === 'Fulfillment' && (
          <section className="orders-page">
            <div className="welcome-row">
              <div>
                <h2>Fulfillment Management</h2>
                <p>
                  Track shipments, delivery progress, carriers and tracking IDs.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </div>

            <div className="order-summary-grid">
              <div className="panel">
                <p>Total fulfillments matching filter</p>
                <h2>{number(fulfillmentTotal)}</h2>
              </div>

              <div className="panel">
                <p>Delivered on this page</p>
                <h2>
                  {number(
                    fulfillments.filter((item) => item.status === 'delivered').length
                  )}
                </h2>
              </div>

              <div className="panel">
                <p>In transit on this page</p>
                <h2>
                  {number(
                    fulfillments.filter((item) => item.status === 'shipped').length
                  )}
                </h2>
              </div>
            </div>

            <div className="panel order-table-panel">
              <div className="order-toolbar">
                <input
                  type="text"
                  placeholder="Search fulfillment, order line, seller or tracking..."
                  value={fulfillmentSearch}
                  onChange={(e) => setFulfillmentSearch(e.target.value)}
                />

                <select
                  value={fulfillmentStatus}
                  onChange={(e) => {
                    setFulfillmentStatus(e.target.value)
                    setFulfillmentOffset(0)
                  }}
                >
                  <option value="all">All statuses</option>
                  <option value="shipped">Shipped</option>
                  <option value="delivered">Delivered</option>
                  <option value="returned">Returned</option>
                </select>
              </div>

              {fulfillmentLoading && (
                <div className="message">Loading fulfillment records...</div>
              )}

              {fulfillmentError && (
                <div className="error-message">
                  {fulfillmentError}
                  <button onClick={loadFulfillments}>Retry</button>
                </div>
              )}

              {!fulfillmentLoading && !fulfillmentError && (
                <>
                  <div className="table-wrapper">
                    <table className="order-table fulfillment-table">
                      <thead>
                        <tr>
                          <th>Fulfillment ID</th>
                          <th>Order Line ID</th>
                          <th>Seller ID</th>
                          <th>Status</th>
                          <th>Carrier</th>
                          <th>Tracking Code</th>
                          <th>Shipped At</th>
                          <th>Delivered At</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredFulfillments.map((item) => (
                          <tr key={item.fulfillment_id}>
                            <td><strong>{item.fulfillment_id}</strong></td>
                            <td>{item.order_line_id}</td>
                            <td>{item.seller_id}</td>
                            <td>
                              <span className={`order-status ${item.status}`}>
                                {item.status}
                              </span>
                            </td>
                            <td>{item.carrier || 'N/A'}</td>
                            <td><strong>{item.tracking_code || 'N/A'}</strong></td>
                            <td>{formatDate(item.shipped_at)}</td>
                            <td>{formatDate(item.delivered_at)}</td>
                          </tr>
                        ))}

                        {filteredFulfillments.length === 0 && (
                          <tr>
                            <td colSpan="8" className="empty-table">
                              No matching fulfillment records found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination">
                    <span>
                      Showing{' '}
                      {fulfillmentTotal === 0 ? 0 : fulfillmentOffset + 1}–
                      {Math.min(
                        fulfillmentOffset + fulfillmentLimit,
                        fulfillmentTotal
                      )}
                      {' '}of {number(fulfillmentTotal)} fulfillments
                    </span>

                    <div>
                      <button
                        disabled={fulfillmentOffset === 0}
                        onClick={() =>
                          setFulfillmentOffset(
                            Math.max(0, fulfillmentOffset - fulfillmentLimit)
                          )
                        }
                      >
                        Previous
                      </button>

                      <button
                        disabled={
                          fulfillmentOffset + fulfillmentLimit >= fulfillmentTotal
                        }
                        onClick={() =>
                          setFulfillmentOffset(
                            fulfillmentOffset + fulfillmentLimit
                          )
                        }
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* DISPUTES MANAGEMENT */}
        {activePage === 'Disputes' && (
          <section className="orders-page">
            <div className="welcome-row">
              <div>
                <h2>Disputes Management</h2>
                <p>
                  Monitor customer complaints, dispute amounts and resolution status.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </div>

            <div className="order-summary-grid">
              <div className="panel">
                <p>Total disputes matching filter</p>
                <h2>{number(disputesTotal)}</h2>
              </div>

              <div className="panel">
                <p>Under review on this page</p>
                <h2>
                  {number(
                    disputes.filter((item) => item.status === 'under_review').length
                  )}
                </h2>
              </div>

              <div className="panel">
                <p>Resolved on this page</p>
                <h2>
                  {number(
                    disputes.filter((item) =>
                      ['closed', 'won', 'lost'].includes(item.status)
                    ).length
                  )}
                </h2>
              </div>
            </div>

            <div className="panel order-table-panel">
              <div className="order-toolbar">
                <input
                  type="text"
                  placeholder="Search dispute, order, seller or reason..."
                  value={disputeSearch}
                  onChange={(e) => setDisputeSearch(e.target.value)}
                />

                <select
                  value={disputeStatus}
                  onChange={(e) => {
                    setDisputeStatus(e.target.value)
                    setDisputeOffset(0)
                  }}
                >
                  <option value="all">All statuses</option>
                  <option value="open">Open</option>
                  <option value="under_review">Under Review</option>
                  <option value="closed">Closed</option>
                  <option value="won">Won</option>
                  <option value="lost">Lost</option>
                </select>
              </div>

              {disputesLoading && (
                <div className="message">Loading dispute records...</div>
              )}

              {disputesError && (
                <div className="error-message">
                  {disputesError}
                  <button onClick={loadDisputes}>Retry</button>
                </div>
              )}

              {!disputesLoading && !disputesError && (
                <>
                  <div className="table-wrapper">
                    <table className="order-table dispute-table">
                      <thead>
                        <tr>
                          <th>Dispute ID</th>
                          <th>Order ID</th>
                          <th>Order Line ID</th>
                          <th>Seller ID</th>
                          <th>Amount</th>
                          <th>Reason</th>
                          <th>Status</th>
                          <th>Opened At</th>
                          <th>Resolved At</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredDisputes.map((item) => (
                          <tr key={item.dispute_id}>
                            <td><strong>{item.dispute_id}</strong></td>
                            <td>{item.order_id}</td>
                            <td>{item.order_line_id || 'N/A'}</td>
                            <td>{item.seller_id}</td>
                            <td><strong>{currency(item.amount)}</strong></td>
                            <td>{item.reason}</td>
                            <td>
                              <span className={`order-status ${item.status}`}>
                                {(item.status || 'unknown').replaceAll('_', ' ')}
                              </span>
                            </td>
                            <td>{formatDate(item.opened_at)}</td>
                            <td>{formatDate(item.resolved_at)}</td>
                          </tr>
                        ))}

                        {filteredDisputes.length === 0 && (
                          <tr>
                            <td colSpan="9" className="empty-table">
                              No matching disputes found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination">
                    <span>
                      Showing{' '}
                      {disputesTotal === 0 ? 0 : disputeOffset + 1}–
                      {Math.min(disputeOffset + disputeLimit, disputesTotal)}
                      {' '}of {number(disputesTotal)} disputes
                    </span>

                    <div>
                      <button
                        disabled={disputeOffset === 0}
                        onClick={() =>
                          setDisputeOffset(
                            Math.max(0, disputeOffset - disputeLimit)
                          )
                        }
                      >
                        Previous
                      </button>

                      <button
                        disabled={disputeOffset + disputeLimit >= disputesTotal}
                        onClick={() =>
                          setDisputeOffset(disputeOffset + disputeLimit)
                        }
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* PAYOUTS MANAGEMENT */}
        {activePage === 'Payouts' && (
          <section className="orders-page">
            <div className="welcome-row">
              <div>
                <h2>Payouts Management</h2>
                <p>
                  Monitor seller payments, payout periods, held amounts and release status.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </div>

            <div className="order-summary-grid">
              <div className="panel">
                <p>Total payouts matching filter</p>
                <h2>{number(payoutsTotal)}</h2>
              </div>

              <div className="panel">
                <p>Held payouts on this page</p>
                <h2>
                  {number(
                    payouts.filter((item) => item.status === 'held').length
                  )}
                </h2>
              </div>

              <div className="panel">
                <p>Total amount on this page</p>
                <h2>
                  {currency(
                    payouts.reduce(
                      (sum, item) => sum + Number(item.total_amount || 0),
                      0
                    )
                  )}
                </h2>
              </div>
            </div>

            <div className="panel order-table-panel">
              <div className="order-toolbar">
                <input
                  type="text"
                  placeholder="Search payout ID or seller ID..."
                  value={payoutSearch}
                  onChange={(e) => setPayoutSearch(e.target.value)}
                />

                <select
                  value={payoutStatus}
                  onChange={(e) => {
                    setPayoutStatus(e.target.value)
                    setPayoutOffset(0)
                  }}
                >
                  <option value="all">All statuses</option>
                  <option value="pending">Pending</option>
                  <option value="held">Held</option>
                  <option value="eligible">Eligible</option>
                  <option value="paid">Paid</option>
                  <option value="failed">Failed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              {payoutsLoading && (
                <div className="message">Loading payout records...</div>
              )}

              {payoutsError && (
                <div className="error-message">
                  {payoutsError}
                  <button onClick={loadPayouts}>Retry</button>
                </div>
              )}

              {!payoutsLoading && !payoutsError && (
                <>
                  <div className="table-wrapper">
                    <table className="order-table payout-table">
                      <thead>
                        <tr>
                          <th>Payout ID</th>
                          <th>Seller ID</th>
                          <th>Period Start</th>
                          <th>Period End</th>
                          <th>Total Amount</th>
                          <th>Status</th>
                          <th>Created At</th>
                          <th>Released At</th>
                        </tr>
                      </thead>

                      <tbody>
                        {filteredPayouts.map((item) => (
                          <tr key={item.payout_id}>
                            <td><strong>{item.payout_id}</strong></td>
                            <td>{item.seller_id}</td>
                            <td>{item.period_start || 'N/A'}</td>
                            <td>{item.period_end || 'N/A'}</td>
                            <td><strong>{currency(item.total_amount)}</strong></td>
                            <td>
                              <span className={`order-status ${item.status}`}>
                                {(item.status || 'unknown').replaceAll('_', ' ')}
                              </span>
                            </td>
                            <td>{formatDate(item.created_at)}</td>
                            <td>{formatDate(item.released_at)}</td>
                          </tr>
                        ))}

                        {filteredPayouts.length === 0 && (
                          <tr>
                            <td colSpan="8" className="empty-table">
                              No matching payout records found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <div className="pagination">
                    <span>
                      Showing{' '}
                      {payoutsTotal === 0 ? 0 : payoutOffset + 1}–
                      {Math.min(payoutOffset + payoutLimit, payoutsTotal)}
                      {' '}of {number(payoutsTotal)} payouts
                    </span>

                    <div>
                      <button
                        disabled={payoutOffset === 0}
                        onClick={() =>
                          setPayoutOffset(
                            Math.max(0, payoutOffset - payoutLimit)
                          )
                        }
                      >
                        Previous
                      </button>

                      <button
                        disabled={payoutOffset + payoutLimit >= payoutsTotal}
                        onClick={() =>
                          setPayoutOffset(payoutOffset + payoutLimit)
                        }
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* OVERVIEW DASHBOARD */}
        {activePage === 'Overview' && data && !loading && (
          <>
            <section className="welcome-row">
              <div>
                <h2>Platform overview</h2>
                <p>
                  Monitor seller activity, orders, fulfillment and payments.
                </p>
              </div>

              <span className="live-label">
                <span className="status-dot" />
                Live database data
              </span>
            </section>

            <section className="stats-grid">
              <StatCard
                title="Total Sellers"
                value={number(data.sellers.total)}
                subtitle={`${number(data.sellers.active)} active sellers`}
                icon={Store}
              />

              <StatCard
                title="Total Orders"
                value={number(data.orders.total)}
                subtitle={`${number(data.orders.total_order_lines)} order lines`}
                icon={ShoppingCart}
              />

              <StatCard
                title="Gross Merchandise Value"
                value={currency(data.orders.gmv)}
                subtitle={`Average order: ${currency(data.orders.average_order_value)}`}
                icon={TrendingUp}
              />

              <StatCard
                title="Total Disputes"
                value={number(data.disputes.total)}
                subtitle={`${number(data.disputes.open)} currently open`}
                icon={AlertTriangle}
              />
            </section>

            <section className="content-grid">
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Fulfillment performance</h3>
                    <p>Order delivery overview</p>
                  </div>
                  <Truck size={20} />
                </div>

                <div className="big-metric">
                  {data.fulfillment.delivery_rate_percent}%
                </div>

                <p className="muted">Overall delivery rate</p>

                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${data.fulfillment.delivery_rate_percent}%`,
                    }}
                  />
                </div>

                <div className="metric-row">
                  <span>Total fulfillments</span>
                  <strong>{number(data.fulfillment.total)}</strong>
                </div>

                <div className="metric-row">
                  <span>Delivered orders</span>
                  <strong>{number(data.fulfillment.delivered)}</strong>
                </div>

                <div className="metric-row">
                  <span>Delivered within 7 days</span>
                  <strong>
                    {data.fulfillment.delivered_within_7_days_percent}%
                  </strong>
                </div>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Seller health</h3>
                    <p>Seller account distribution</p>
                  </div>
                  <Activity size={20} />
                </div>

                <div className="big-metric">
                  {number(data.sellers.total)}
                </div>

                <p className="muted">Registered sellers</p>

                <div className="seller-bar">
                  <div
                    className="seller-active"
                    style={{
                      width: `${
                        data.sellers.total
                          ? (data.sellers.active / data.sellers.total) * 100
                          : 0
                      }%`,
                    }}
                  />

                  <div
                    className="seller-suspended"
                    style={{
                      width: `${
                        data.sellers.total
                          ? (data.sellers.suspended / data.sellers.total) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>

                <div className="legend-row">
                  <span>
                    <i className="legend-active" /> Active
                  </span>
                  <strong>{number(data.sellers.active)}</strong>
                </div>

                <div className="legend-row">
                  <span>
                    <i className="legend-suspended" /> Suspended
                  </span>
                  <strong>{number(data.sellers.suspended)}</strong>
                </div>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Dispute monitoring</h3>
                    <p>Customer dispute overview</p>
                  </div>
                  <AlertTriangle size={20} />
                </div>

                <div className="big-metric">
                  {data.disputes.dispute_rate_percent}%
                </div>

                <p className="muted">Dispute rate</p>

                <div className="metric-row">
                  <span>Total disputes</span>
                  <strong>{number(data.disputes.total)}</strong>
                </div>

                <div className="metric-row">
                  <span>Open disputes</span>
                  <strong className="warning-text">
                    {number(data.disputes.open)}
                  </strong>
                </div>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Payout monitoring</h3>
                    <p>Seller payment summary</p>
                  </div>
                  <Wallet size={20} />
                </div>

                <div className="big-metric">
                  {number(data.payouts.total)}
                </div>

                <p className="muted">Payout records</p>

                <div className="metric-row">
                  <span>Held amount</span>
                  <strong>{currency(data.payouts.held_amount)}</strong>
                </div>

                <div className="metric-row">
                  <span>Eligible amount</span>
                  <strong>{currency(data.payouts.eligible_amount)}</strong>
                </div>

                <div className="metric-row">
                  <span>Paid amount</span>
                  <strong>{currency(data.payouts.paid_amount)}</strong>
                </div>
              </div>
            </section>

            <section className="bottom-grid">
              <div className="panel rating-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Customer feedback</h3>
                    <p>Seller review statistics</p>
                  </div>
                  <Star size={20} />
                </div>

                <div className="rating-value">
                  {data.reviews.average_rating}
                  <span>/ 5</span>
                </div>

                <p className="muted">
                  Based on {number(data.reviews.total)} customer reviews
                </p>
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Platform data</h3>
                    <p>Current database snapshot</p>
                  </div>
                  <Package size={20} />
                </div>

                <div className="metric-row">
                  <span>Order lines</span>
                  <strong>{number(data.orders.total_order_lines)}</strong>
                </div>

                <div className="metric-row">
                  <span>Reviews</span>
                  <strong>{number(data.reviews.total)}</strong>
                </div>

                <div className="metric-row">
                  <span>Suspended sellers</span>
                  <strong>{number(data.sellers.suspended)}</strong>
                </div>
              </div>
            </section>

            <footer>
              Seller Operations Platform · Dashboard data from FastAPI + SQLite
            </footer>
          </>
        )}

        {/* Remaining pages */}
        {![
          'Overview',
          'Sellers',
          'Orders',
          'Fulfillment',
          'Disputes',
          'Payouts',
        ].includes(activePage) && (
          <div
            className="panel"
            style={{ padding: '35px', marginTop: '25px' }}
          >
            <h2>{activePage} Management</h2>
            <p className="muted">
              This section is the next development step. The backend API
              will be connected when we build this page.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
